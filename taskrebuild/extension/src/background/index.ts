import { recordTaskActivity, checkAllMonitored } from '../lib/api';

console.log('TaskRebuild background service started');

// Local buffer for events
let eventBuffer: any[] = [];
let activeTaskId: string | null = null;
let flushInterval: any = null;

// Initialize state
chrome.storage.local.get(['activeTaskId'], (result) => {
  if (result.activeTaskId) {
    activeTaskId = result.activeTaskId;
    startFlushing();
  }
});

// Listen for storage changes to active task
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'local' && changes.activeTaskId) {
    activeTaskId = changes.activeTaskId.newValue || null;
    
    if (activeTaskId) {
      startFlushing();
    } else {
      stopFlushing();
      eventBuffer = []; // Clear buffer if task is stopped
    }
  }
});

function startFlushing() {
  if (!flushInterval) {
    // Flush every 20 seconds
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
    // On failure, prepend back to buffer (with a limit to prevent memory leak)
    if (eventBuffer.length < 500) {
      eventBuffer = [...eventsToSend, ...eventBuffer];
    }
  }
}

function handleEvent(eventType: string, tab: chrome.tabs.Tab) {
  if (!activeTaskId) return; // Only capture if a task is active
  
  // Ignore events without a valid http/https URL (e.g. chrome:// tabs)
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
  
  // Real-time flush for testing
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
  
  // For removed tabs, we don't have the tab object anymore, so we construct a partial event
  const event = {
    event_type: 'tab_closed',
    tab_id: String(tabId),
    window_id: String(removeInfo.windowId),
    timestamp: new Date().toISOString()
  };
  
  eventBuffer.push(event);
  flushEvents();
});


// --- Phase 7 Automated Resource Monitoring ---

// Listen for messages from popup to enable/disable monitor
chrome.runtime.onMessage.addListener((message, _sender, _sendResponse) => {
  if (message.type === 'ENABLE_RESOURCE_MONITOR') {
    chrome.alarms.get('resourceMonitor', (alarm) => {
      if (!alarm) {
        chrome.alarms.create('resourceMonitor', { periodInMinutes: 60 });
        console.log('Resource Monitor alarm created (60 min)');
      }
    });
  }
});

// Create alarm on install if active task requires it (we just start it globally for safety)
chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create('resourceMonitor', { periodInMinutes: 60 });
});

// Alarm Listener
chrome.alarms.onAlarm.addListener(async (alarm) => {
  if (alarm.name === 'resourceMonitor') {
    console.log('Resource Monitor alarm triggered');
    try {
      const data = await checkAllMonitored();
      if (data && data.alerts && data.alerts.length > 0) {
        chrome.notifications.create({
          type: 'basic',
          iconUrl: chrome.runtime.getURL('icon48.png'), // Add an icon if exists
          title: 'TaskRebuild: Resource Alerts',
          message: `${data.alerts.length} resource(s) went offline or changed. Check your task alerts!`,
          priority: 2
        });
      }
    } catch (err) {
      console.error('Failed automated check:', err);
    }
  }
});
