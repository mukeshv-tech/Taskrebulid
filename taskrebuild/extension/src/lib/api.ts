export const getApiBaseUrl = () => import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${getApiBaseUrl()}${endpoint}`;
  
  // Get token from local storage (set by Supabase auth in popup)
  const sessionString = localStorage.getItem('supabase-session');
  let token = '';
  if (sessionString) {
    try {
      const session = JSON.parse(sessionString);
      token = session?.access_token || '';
    } catch (e) {
      console.error('Error parsing session', e);
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
