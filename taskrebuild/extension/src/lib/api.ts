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
