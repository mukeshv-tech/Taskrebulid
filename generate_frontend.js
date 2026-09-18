const fs = require('fs');
const path = require('path');

const basePath = path.join(__dirname, 'taskrebuild', 'extension');

const files = {
  '.env': `VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
`,
  '.env.example': `VITE_API_BASE_URL=http://localhost:8000
VITE_SUPABASE_URL=
VITE_SUPABASE_ANON_KEY=
`,
  'src/lib/api.ts': `export const getApiBaseUrl = () => import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
  const url = \`\${getApiBaseUrl()}\${endpoint}\`;
  
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
    headers.set('Authorization', \`Bearer \${token}\`);
  }
  headers.set('Content-Type', 'application/json');

  const res = await fetch(url, { ...options, headers });
  if (!res.ok) {
    throw new Error(\`API Error: \${res.status} \${res.statusText}\`);
  }
  
  return res.json();
};
`,
  'src/lib/supabase.ts': `import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || '';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
`,
  'src/popup/App.tsx': `import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { fetchApi } from '../lib/api';

const App: React.FC = () => {
  const [session, setSession] = useState<any>(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [tasks, setTasks] = useState<any[]>([]);
  const [newTaskName, setNewTaskName] = useState('');

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      if (session) {
        localStorage.setItem('supabase-session', JSON.stringify(session));
        loadTasks();
      }
    });

    supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
      if (session) {
        localStorage.setItem('supabase-session', JSON.stringify(session));
        loadTasks();
      } else {
        localStorage.removeItem('supabase-session');
        setTasks([]);
      }
    });
  }, []);

  const loadTasks = async () => {
    try {
      const data = await fetchApi('/api/tasks');
      setTasks(data);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSignUp = async () => {
    setLoading(true);
    const { error } = await supabase.auth.signUp({ email, password });
    if (error) alert(error.message);
    setLoading(false);
  };

  const handleSignIn = async () => {
    setLoading(true);
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) alert(error.message);
    setLoading(false);
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
  };

  const handleCreateTask = async () => {
    if (!newTaskName) return;
    try {
      await fetchApi('/api/tasks', {
        method: 'POST',
        body: JSON.stringify({ name: newTaskName })
      });
      setNewTaskName('');
      loadTasks();
    } catch (e) {
      console.error(e);
      alert('Failed to create task');
    }
  };

  const handleDeleteTask = async (id: string) => {
    try {
      await fetchApi(\`/api/tasks/\${id}\`, { method: 'DELETE' });
      loadTasks();
    } catch (e) {
      console.error(e);
    }
  };

  if (!session) {
    return (
      <div className="popup-container">
        <h1>TaskRebuild</h1>
        <p>Your browser remembers the work, not just the tabs.</p>
        
        <div className="status-section">
          <span className="status-label">Status:</span>
          <span className="status-value">Signed out</span>
        </div>
        
        <div className="auth-form">
          <label>Email:</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} />
          
          <label>Password:</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} />
          
          <div className="auth-buttons">
            <button onClick={handleSignIn} disabled={loading}>Sign In</button>
            <button onClick={handleSignUp} disabled={loading}>Create Account</button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="popup-container">
      <h1>TaskRebuild</h1>
      <p>Signed in as: <br/><strong>{session.user.email}</strong></p>
      
      <div className="status-section">
        <span className="status-label">Status:</span>
        <span className="status-value connected">Connected</span>
      </div>
      
      <div className="tasks-section">
        <h3>Your Tasks</h3>
        <ul className="task-list">
          {tasks.map(t => (
            <li key={t.id}>
              {t.name}
              <button onClick={() => handleDeleteTask(t.id)}>x</button>
            </li>
          ))}
        </ul>
        <div className="new-task-form">
          <input 
            type="text" 
            placeholder="New Task Name" 
            value={newTaskName}
            onChange={e => setNewTaskName(e.target.value)}
          />
          <button className="new-task-btn" onClick={handleCreateTask}>+ New Task</button>
        </div>
      </div>

      <button className="sign-out-btn" onClick={handleSignOut}>Sign Out</button>
    </div>
  );
};

export default App;
`,
  'src/popup/styles.css': `body {
  margin: 0;
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  width: 300px;
  background-color: #f9fafb;
  color: #111827;
}

.popup-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

p {
  margin: 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.4;
  word-break: break-all;
}

.status-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #e5e7eb;
  border-radius: 6px;
}

.status-label {
  font-size: 13px;
  font-weight: 600;
}

.status-value {
  font-size: 13px;
  color: #4b5563;
  font-weight: 500;
}

.status-value.connected {
  color: #059669;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.auth-form label {
  font-size: 12px;
  font-weight: 600;
}

.auth-form input, .new-task-form input {
  padding: 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.auth-buttons {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}

.auth-buttons button, .sign-out-btn {
  flex: 1;
  padding: 8px;
  background-color: #e5e7eb;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
}

.new-task-btn {
  margin-top: 8px;
  padding: 10px;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.new-task-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.tasks-section h3 {
  font-size: 14px;
  margin: 8px 0;
}

.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-list li {
  display: flex;
  justify-content: space-between;
  background: white;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  font-size: 14px;
}

.task-list li button {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-weight: bold;
}
`
};

function ensureDirSync(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

for (const [relativePath, content] of Object.entries(files)) {
  const fullPath = path.join(basePath, relativePath);
  ensureDirSync(path.dirname(fullPath));
  fs.writeFileSync(fullPath, content, 'utf8');
}
console.log('Frontend files generated.');
