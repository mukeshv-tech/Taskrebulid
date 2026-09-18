import React, { useState, useEffect } from 'react';

import { fetchApi } from '../lib/api';

const App: React.FC = () => {
  const [session, setSession] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [newTaskName, setNewTaskName] = useState('');
  const [selectedTask, setSelectedTask] = useState<any>(null);

  useEffect(() => {
    // HARDCODED BYPASS FOR TESTING
    const dummySession = {
      access_token: 'PASTE_YOUR_USER_JWT_HERE',
      user: { id: 'c96c1bfb-3c54-4400-b162-22e2eb5d5220', email: 'mukesh.v@globalschoolsalumni.org' }
    };
    setSession(dummySession);
    localStorage.setItem('supabase-session', JSON.stringify(dummySession));
    
    // We delay loadTasks slightly so the state sets
    setTimeout(() => {
      loadTasks();
    }, 500);
  }, []);

  const loadTasks = async () => {
    try {
      const data = await fetchApi('/api/tasks');
      setTasks(data);
    } catch (e) {
      console.error(e);
    }
  };
  
  const handleSignOut = async () => {
    // Hardcoded out
    setSession(null);
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

  const handleDeleteTask = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // Prevent opening the task when clicking delete
    try {
      await fetchApi(`/api/tasks/${id}`, { method: 'DELETE' });
      if (selectedTask?.id === id) setSelectedTask(null);
      loadTasks();
    } catch (e) {
      console.error(e);
    }
  };

  // Wait for dummy session to initialize
  if (!session) return null;

  if (selectedTask) {
    return (
      <div className="popup-container">
        <button className="back-btn" onClick={() => setSelectedTask(null)}>← Back to tasks</button>
        <h2>📁 {selectedTask.name}</h2>
        <p style={{ fontSize: '12px', color: '#6b7280' }}>
          Created: {new Date(selectedTask.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        </p>
        
        <div className="task-resources">
          <h4>Resources:</h4>
          <p>None yet.</p>
        </div>
        
        <div className="task-activity-note">
          <p><em>This task has no captured browser activity yet.</em></p>
        </div>
        
        <button className="delete-task-btn" onClick={(e) => handleDeleteTask(e, selectedTask.id)}>Delete Task</button>
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
        <h3>My Tasks</h3>
        <ul className="task-list">
          {tasks.map(t => (
            <li key={t.id} onClick={() => setSelectedTask(t)} style={{ cursor: 'pointer' }}>
              <span>📁 {t.name}</span>
              <button onClick={(e) => handleDeleteTask(e, t.id)}>x</button>
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
