import { supabase } from './supabase';

export const getApiBaseUrl = () => 'https://taskrebulid.onrender.com';

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${getApiBaseUrl()}${endpoint}`;
  
  let token = '';
  
  // 1. Try localStorage first (popup environment usually has window)
  if (typeof window !== 'undefined' && window.localStorage) {
    const sessionString = window.localStorage.getItem('supabase-session');
    if (sessionString) {
      try {
        const session = JSON.parse(sessionString);
        token = session?.access_token || '';
      } catch (e) {
        console.error('Error parsing session from localStorage', e);
      }
    }
  }

  // 2. Fallback to chrome.storage.local if token not found
  if (!token && typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    try {
      const result = await new Promise<any>((resolve) => {
        chrome.storage.local.get(['supabase-session'], resolve);
      });
      const sessionString = result?.['supabase-session'];
      if (sessionString) {
        const session = typeof sessionString === 'string' ? JSON.parse(sessionString) : sessionString;
        token = session?.access_token || '';
      }
    } catch (e) {
      console.error('Error parsing session from chrome.storage', e);
    }
  }

  // 3. Fallback directly to supabase auth client session
  if (!token) {
    try {
      const { data } = await supabase.auth.getSession();
      if (data?.session?.access_token) {
        token = data.session.access_token;
      }
    } catch (e) {
      console.error('Error getting session from supabase client', e);
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

export const generateClusters = (taskId: string) => fetchApi(`/api/tasks/${taskId}/clusters/generate`, { method: 'POST' });
export const getClusters = (taskId: string) => fetchApi(`/api/tasks/${taskId}/clusters`);

// Phase 9: Personal Knowledge System API
export const listKnowledge = (params: { type?: string, status?: string, task_id?: string, source_id?: string, limit?: number, offset?: number } = {}) => {
  const query = new URLSearchParams();
  if (params.type) query.set('type', params.type);
  if (params.status) query.set('status', params.status);
  if (params.task_id) query.set('task_id', params.task_id);
  if (params.source_id) query.set('source_id', params.source_id);
  if (params.limit) query.set('limit', String(params.limit));
  if (params.offset) query.set('offset', String(params.offset));
  return fetchApi(`/api/knowledge?${query.toString()}`);
};

export const getKnowledgeDetail = (id: string) => fetchApi(`/api/knowledge/${id}`);

export const createKnowledge = (data: {
  type: string;
  title: string;
  content: string;
  summary?: string;
  origin?: string;
  confidence?: number;
  sources?: any[];
  related_knowledge_ids?: string[];
}) => fetchApi('/api/knowledge', { method: 'POST', body: JSON.stringify(data) });

export const updateKnowledge = (id: string, data: { title?: string; type?: string; content?: string; summary?: string }) =>
  fetchApi(`/api/knowledge/${id}`, { method: 'PATCH', body: JSON.stringify(data) });

export const deleteKnowledge = (id: string) => fetchApi(`/api/knowledge/${id}`, { method: 'DELETE' });

export const archiveKnowledge = (id: string) => fetchApi(`/api/knowledge/${id}/archive`, { method: 'POST' });
export const restoreKnowledge = (id: string) => fetchApi(`/api/knowledge/${id}/restore`, { method: 'POST' });

export const checkKnowledgeDuplicate = (title: string) =>
  fetchApi('/api/knowledge/check-duplicate', { method: 'POST', body: JSON.stringify({ title }) });

export const getKnowledgeRelatedGraph = (id: string, depth = 1) =>
  fetchApi(`/api/knowledge/${id}/related?depth=${depth}`);

export const createKnowledgeRelationship = (id: string, target_knowledge_id: string, relationship_type: string) =>
  fetchApi(`/api/knowledge/${id}/relationships`, {
    method: 'POST',
    body: JSON.stringify({ target_knowledge_id, relationship_type })
  });

export const deleteKnowledgeRelationship = (id: string, relationshipId: string) =>
  fetchApi(`/api/knowledge/${id}/relationships/${relationshipId}`, { method: 'DELETE' });

export const getKnowledgeSources = (id: string) => fetchApi(`/api/knowledge/${id}/sources`);

export const addKnowledgeSource = (id: string, source: { source_type: string; source_id?: string; source_name?: string; metadata?: any }) =>
  fetchApi(`/api/knowledge/${id}/sources`, { method: 'POST', body: JSON.stringify(source) });

export const deleteKnowledgeSource = (id: string, sourceId: string) =>
  fetchApi(`/api/knowledge/${id}/sources/${sourceId}`, { method: 'DELETE' });

export const getTaskKnowledgeSuggestions = (taskId: string) =>
  fetchApi(`/api/tasks/${taskId}/knowledge/suggestions`, { method: 'POST' });

export const saveTaskAsKnowledge = (taskId: string, data: {
  title: string;
  type?: string;
  content?: string;
  summary?: string;
  include_summary_as_source?: boolean;
  include_task_as_source?: boolean;
}) => fetchApi(`/api/tasks/${taskId}/knowledge/save-from-task`, { method: 'POST', body: JSON.stringify(data) });

export const saveResourceAsKnowledge = (taskId: string, resourceId: string, data: {
  title?: string;
  type?: string;
  content?: string;
  summary?: string;
}) => fetchApi(`/api/tasks/${taskId}/knowledge/resources/${resourceId}/save-as-knowledge`, { method: 'POST', body: JSON.stringify(data) });
