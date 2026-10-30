import { recordTaskActivity, createKnowledge, createTaskResource, getTasks } from '../lib/api';

console.log('TaskRebuild background service started');

// Local buffer for events
let eventBuffer: any[] = [];
let activeTaskId: string | null = null;
let activeTaskName: string | null = null;
let flushInterval: any = null;

// Initialize state
chrome.storage.local.get(['activeTaskId', 'activeTaskName'], (result) => {
  if (result.activeTaskId) {
    activeTaskId = result.activeTaskId;
    activeTaskName = result.activeTaskName || null;
    startFlushing();
  }
});

// Listen for storage changes to active task
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local') {
    if (changes.activeTaskId) {
      activeTaskId = changes.activeTaskId.newValue || null;
      if (activeTaskId) {
        startFlushing();
      } else {
        stopFlushing();
        eventBuffer = []; // Clear buffer if task is stopped
      }
    }
    if (changes.activeTaskName) {
      activeTaskName = changes.activeTaskName.newValue || null;
    }
  }
});

function startFlushing() {
  if (!flushInterval) {
    flushInterval = setInterval(flushEvents, 20000);
  }
}

function stopFlushing() {
  if (flushInterval) {
    clearInterval(flushInterval);
    flushInterval = null;
  }
}

async function flushEvents() {
  if (!activeTaskId || eventBuffer.length === 0) return;
  
  const eventsToSend = [...eventBuffer];
  eventBuffer = []; // Clear current buffer
  
  try {
    await recordTaskActivity(activeTaskId, eventsToSend);
    console.log(`Flushed ${eventsToSend.length} events for task ${activeTaskId}`);
  } catch (error) {
    console.error('Failed to flush events', error);
    if (eventBuffer.length < 500) {
      eventBuffer = [...eventsToSend, ...eventBuffer];
    }
  }
}

function handleEvent(eventType: string, tab: chrome.tabs.Tab) {
  if (!activeTaskId) return;
  if (!tab.url || !tab.url.startsWith('http')) return;
  
  const event = {
    event_type: eventType,
    url: tab.url,
    title: tab.title || '',
    tab_id: String(tab.id),
    window_id: String(tab.windowId),
    timestamp: new Date().toISOString()
  };
  
  eventBuffer.push(event);
  flushEvents();
}

// Listen to Chrome events
chrome.tabs.onUpdated.addListener((_tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' || changeInfo.url) {
    handleEvent('navigation', tab);
  }
});

chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    handleEvent('tab_activated', tab);
  } catch (e) {
    console.error(e);
  }
});

chrome.tabs.onCreated.addListener((tab) => {
  handleEvent('tab_created', tab);
});

chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
  if (!activeTaskId) return;
  const event = {
    event_type: 'tab_closed',
    tab_id: String(tabId),
    window_id: String(removeInfo.windowId),
    timestamp: new Date().toISOString()
  };
  eventBuffer.push(event);
  flushEvents();
});

// Runtime messages from content script (Floating Capture)
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message.action === 'GET_ACTIVE_CONTEXT') {
    chrome.storage.local.get(['activeTaskId', 'activeTaskName', 'supabase-session'], async (res) => {
      let tasksList: any[] = [];
      if (res['supabase-session']) {
        try {
          tasksList = await getTasks();
        } catch (e) {
          console.error('Failed to fetch tasks for context', e);
        }
      }
      sendResponse({
        activeTaskId: res.activeTaskId || null,
        activeTaskName: res.activeTaskName || null,
        hasSession: !!res['supabase-session'],
        tasks: Array.isArray(tasksList) ? tasksList : []
      });
    });
    return true; // Keep message channel open for async response
  }

  if (message.action === 'SET_ACTIVE_TASK') {
    const { taskId, taskName } = message.payload;
    chrome.storage.local.set({ activeTaskId: taskId, activeTaskName: taskName }, () => {
      activeTaskId = taskId;
      activeTaskName = taskName;
      sendResponse({ success: true });
    });
    return true;
  }

  if (message.action === 'SAVE_KNOWLEDGE_CAPTURE') {
    const { title, content, type, url, pageTitle, taskId, taskName } = message.payload;
    const sources: any[] = [];
    if (taskId) {
      sources.push({
        source_type: 'task',
        source_id: taskId,
        source_name: taskName || activeTaskName || 'Selected Task'
      });
    }
    if (url) {
      sources.push({
        source_type: 'resource',
        source_name: pageTitle || url,
        metadata: { url }
      });
    }

    createKnowledge({
      title,
      content,
      type: type || 'note',
      sources
    })
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message || 'Failed to save knowledge' }));

    return true;
  }

  if (message.action === 'SAVE_RESOURCE_CAPTURE') {
    const { taskId, url, title } = message.payload;
    if (!taskId) {
      sendResponse({ success: false, error: 'Please choose a target task first' });
      return true;
    }

    createTaskResource(taskId, { url, title })
      .then((data) => sendResponse({ success: true, data }))
      .catch((err) => sendResponse({ success: false, error: err.message || 'Failed to save resource' }));

    return true;
  }
});
