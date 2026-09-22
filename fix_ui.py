import codecs
import re

path = 'taskrebuild/extension/src/popup/components/ResourceMonitor.tsx'
code = codecs.open(path, 'r', 'utf-8').read()

import_rep = '''import { getTaskResourcesStatus, triggerResourceCheck, analyzeResourceReplacement, replaceResourceWithExisting, getTaskActivity, dismissResourceAlert, toggleAutoMonitor } from '../../lib/api';'''
code = re.sub(r"import \{.*?\} from '\.\./\.\./lib/api';", import_rep, code)

state_rep = '''  const [resources, setResources] = useState<any[]>([]);
  const [activities, setActivities] = useState<any[]>([]);
  const [autoMonitor, setAutoMonitor] = useState<boolean>(false);'''
code = code.replace('''  const [resources, setResources] = useState<any[]>([]);
  const [activities, setActivities] = useState<any[]>([]);''', state_rep)

fetch_rep = '''  const fetchResources = async () => {
    try {
      setLoading(true);
      const data = await getTaskResourcesStatus(taskId);
      setResources(data.resources || []);
      setAutoMonitor(data.auto_monitor_enabled || false);
      const actData = await getTaskActivity(taskId);
      setActivities(actData || []);'''
code = code.replace('''  const fetchResources = async () => {
    try {
      setLoading(true);
      const data = await getTaskResourcesStatus(taskId);
      setResources(data.resources || []);
      const actData = await getTaskActivity(taskId);
      setActivities(actData || []);''', fetch_rep)

toggle_func = '''  const handleToggleAutoMonitor = async () => {
    try {
      const data = await toggleAutoMonitor(taskId);
      setAutoMonitor(data.auto_monitor_enabled);
      
      // Update background alarm state if enabled
      if (data.auto_monitor_enabled) {
        chrome.runtime.sendMessage({ type: 'ENABLE_RESOURCE_MONITOR' });
      }
    } catch (err: any) {
      console.error(err);
      alert('Failed to toggle auto-monitor: ' + err.message);
    }
  };

  const getStatusDisplay'''
code = code.replace('  const getStatusDisplay', toggle_func)

header_rep = '''    return (
      <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #e5e7eb', borderRadius: '8px', backgroundColor: '#fff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h3 style={{ margin: 0, color: '#111827' }}>RESOURCE ALERTS</h3>
          <button 
            onClick={handleToggleAutoMonitor}
            style={{ 
              fontSize: '11px', padding: '4px 10px', borderRadius: '12px', border: 'none', cursor: 'pointer',
              background: autoMonitor ? '#10b981' : '#e5e7eb',
              color: autoMonitor ? 'white' : '#4b5563',
              fontWeight: 600
            }}
          >
            {autoMonitor ? 'Auto-Monitor: ON' : 'Auto-Monitor: OFF'}
          </button>
        </div>
        {error && <p style={{ color: 'red', fontSize: '12px' }}>{String(error)}</p>}
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>'''
code = code.replace('''    return (
      <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #e5e7eb', borderRadius: '8px', backgroundColor: '#fff' }}>
        <h3 style={{ marginTop: 0, color: '#111827' }}>RESOURCE ALERTS</h3>
        {error && <p style={{ color: 'red', fontSize: '12px' }}>{String(error)}</p>}
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>''', header_rep)


with open(path, 'w', encoding='utf-8') as f:
    f.write(code)
