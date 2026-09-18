import React, { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { fetchApi } from '../lib/api';
import { Provider } from '@supabase/supabase-js';

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
  
  const handleOAuthSignIn = async (provider: Provider) => {
    setLoading(true);
    try {
      // 1. Get the extension's unique redirect URL
      const redirectUrl = chrome.identity.getRedirectURL();
      
      // 2. Ask Supabase for the OAuth URL (do not redirect automatically)
      const { data, error } = await supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: redirectUrl,
          skipBrowserRedirect: true,
        },
      });

      if (error) throw error;
      if (!data?.url) throw new Error('No OAuth URL returned');

      // 3. Launch Chrome's secure web auth flow
      chrome.identity.launchWebAuthFlow(
        {
          url: data.url,
          interactive: true,
        },
        async (responseUrl: string | undefined) => {
          if (chrome.runtime.lastError || !responseUrl) {
            console.error(chrome.runtime.lastError);
            setLoading(false);
            return;
          }

          // 4. Parse the tokens from the response URL hash
          const url = new URL(responseUrl);
          const hashParams = new URLSearchParams(url.hash.substring(1));
          const access_token = hashParams.get('access_token');
          const refresh_token = hashParams.get('refresh_token');

          if (access_token && refresh_token) {
            // 5. Tell Supabase we logged in!
            const { error: sessionError } = await supabase.auth.setSession({
              access_token,
              refresh_token,
            });
            if (sessionError) {
              console.error('Session Error:', sessionError);
              alert(sessionError.message);
            }
          } else {
            console.error('No tokens found in response', responseUrl);
          }
          setLoading(false);
        }
      );
    } catch (err: any) {
      console.error(err);
      alert(err.message);
      setLoading(false);
    }
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
      await fetchApi(`/api/tasks/${id}`, { method: 'DELETE' });
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
          <button className="oauth-btn" onClick={() => handleOAuthSignIn('google')} disabled={loading}>
            Sign in with Google
          </button>
          
          <div className="divider"><span>OR</span></div>
          
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
