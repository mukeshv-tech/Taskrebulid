export const getApiBaseUrl = () => 'https://taskrebulid.onrender.com';

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${getApiBaseUrl()}${endpoint}`;
  
  let token = '';
  
  // Try localStorage first (popup environment usually has window)
  if (typeof window !== 'undefined' && window.localStorage) {
    const sessionString = window.localStorage.getItem('supabase-session');
    if (sessionString) {
      try {
        const session = JSON.parse(sessionString);
        token = session?.access_token || '';
      } catch (e) {
        console.error('Error parsing session', e);
      }
    }
  } else if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    // Fallback to chrome.storage.local (background script)
    const result = await new Promise<any>((resolve) => {
      chrome.storage.local.get(['supabase-session'], resolve);
    });
    const sessionString = result['supabase-session'];
    if (sessionString) {
      try {
        const session = JSON.parse(sessionString);
        token = session?.access_token || '';
      } catch (e) {
        console.error('Error parsing session from chrome.storage', e);
      }
    }
  }

  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  headers.set('Content-Type', 'application/json');

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`);
  }
  
  return res.json();
};

export const getTasks = () => fetchApi('/api/tasks');
export const createTask = (name: string) => fetchApi('/api/tasks', { method: 'POST', body: JSON.stringify({ name }) });
export const deleteTask = (taskId: string) => fetchApi(`/api/tasks/${taskId}`, { method: 'DELETE' });

export const getTaskResources = (taskId: string) => fetchApi(`/api/tasks/${taskId}/resources`);
export const createTaskResource = (taskId: string, resource: { url: string, title?: string }) => fetchApi(`/api/tasks/${taskId}/resources`, { method: 'POST', body: JSON.stringify(resource) });
export const deleteTaskResource = (taskId: string, resourceId: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}`, { method: 'DELETE' });

export const getTaskActivity = (taskId: string) => fetchApi(`/api/tasks/${taskId}/activity`);
export const recordTaskActivity = (taskId: string, events: any[]) => fetchApi(`/api/tasks/${taskId}/activity`, { method: 'POST', body: JSON.stringify({ events }) });
export const deleteTaskActivity = (taskId: string, activityId: string) => fetchApi(`/api/tasks/${taskId}/activity/${activityId}`, { method: 'DELETE' });
export const clearTaskActivity = (taskId: string) => fetchApi(`/api/tasks/${taskId}/activity`, { method: 'DELETE' });

export const analyzeTask = (taskId: string) => {
  const url = `/api/tasks/${taskId}/ai/analyze`;
  return fetchApi(url, { method: 'POST' });
};
export const getTaskAIAnalyses = (taskId: string) => fetchApi(`/api/tasks/${taskId}/ai/analyses`);
export const deleteTaskAIAnalysis = (taskId: string) => fetchApi(`/api/tasks/${taskId}/ai/analyses`, { method: 'DELETE' });

export const getTaskGraph = (taskId: string) => fetchApi(`/api/tasks/${taskId}/graph`);
export const analyzeTaskGraph = (taskId: string) => fetchApi(`/api/tasks/${taskId}/graph/analyze`, { method: 'POST' });
export const deleteGraphNode = (taskId: string, nodeId: string) => fetchApi(`/api/tasks/${taskId}/graph/nodes/${nodeId}`, { method: 'DELETE' });
export const deleteGraphEdge = (taskId: string, edgeId: string) => fetchApi(`/api/tasks/${taskId}/graph/edges/${edgeId}`, { method: 'DELETE' });
export const rejectGraphEdge = (taskId: string, edgeId: string) => fetchApi(`/api/tasks/${taskId}/graph/edges/${edgeId}/reject`, { method: 'POST' });

export const getTaskResume = (taskId: string) => fetchApi(`/api/tasks/${taskId}/resume`);
export const analyzeTaskResume = (taskId: string) => fetchApi(`/api/tasks/${taskId}/resume/analyze`, { method: 'POST' });
export const deleteTaskResume = (taskId: string) => fetchApi(`/api/tasks/${taskId}/resume`, { method: 'DELETE' });
export const getTaskSnapshots = (taskId: string) => fetchApi(`/api/tasks/${taskId}/snapshots`);
export const getTaskSnapshot = (taskId: string, snapshotId: string) => fetchApi(`/api/tasks/${taskId}/snapshots/${snapshotId}`);
export const restoreWorkspace = (taskId: string, urls: string[]) => fetchApi(`/api/tasks/${taskId}/workspace/restore`, { method: 'POST', body: JSON.stringify({ urls }) });

// Phase 7: Monitoring API
export const getTaskResourcesStatus = (taskId: string) => fetchApi(`/api/tasks/${taskId}/resources/status`);
export const getResourceChecks = (taskId: string, resourceId: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/checks`);
export const toggleResourceIgnore = (taskId: string, resourceId: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/toggle-ignore`, { method: 'POST' });
export const triggerResourceCheck = (taskId: string, resourceId: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/check`, { method: 'POST' });
export const dismissResourceAlert = (taskId: string, resourceId: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/dismiss-alert`, { method: 'POST' });
export const analyzeResourceReplacement = (taskId: string, resourceId: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/replacement-analysis`, { method: 'POST' });
export const replaceResource = (taskId: string, resourceId: string, replacementUrl: string, replacementTitle?: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/replace`, { method: 'POST', body: JSON.stringify({ replacement_url: replacementUrl, replacement_title: replacementTitle }) });
export const replaceResourceWithExisting = (taskId: string, resourceId: string, newUrl: string, newTitle?: string) => fetchApi(`/api/tasks/${taskId}/resources/${resourceId}/replace`, { method: 'POST', body: JSON.stringify({ new_url: newUrl, new_title: newTitle }) });

export const toggleAutoMonitor = (taskId: string) => fetchApi(`/api/tasks/${taskId}/toggle-monitor`, { method: 'POST' });
export const checkAllMonitored = () => fetchApi(`/api/monitoring/check-all`, { method: 'POST' });

export const generateLearningPath = (taskId: string) => fetchApi(`/api/tasks/${taskId}/learning-path`, { method: 'POST' });
export const getLearningPath = (taskId: string) => fetchApi(`/api/tasks/${taskId}/learning-path`);

export const generateClusters = (taskId: string) => fetchApi(`/api/tasks/${taskId}/clusters`, { method: 'POST' });
export const getClusters = (taskId: string) => fetchApi(`/api/tasks/${taskId}/clusters`);
