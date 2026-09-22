import codecs

path = 'taskrebuild/extension/src/background/index.ts'
code = codecs.open(path, 'r', 'utf-8').read()

import_rep = '''import { recordTaskActivity, checkAllMonitored } from '../lib/api';'''
code = code.replace("import { recordTaskActivity } from '../lib/api';", import_rep)

alarms_code = '''
// --- Phase 7 Automated Resource Monitoring ---

// Listen for messages from popup to enable/disable monitor
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
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
'''

code += '\n' + alarms_code

with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
