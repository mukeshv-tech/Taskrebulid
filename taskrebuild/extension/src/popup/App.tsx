import React, { useState, useEffect } from 'react';
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
          <p style={{ fontSize: '13px', color: '#6b7280' }}>
            <em>Authentication UI temporarily removed.</em>
          </p>
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
