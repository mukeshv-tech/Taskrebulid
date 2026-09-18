import React, { useState, useEffect } from 'react';
import { fetchApi, getTaskResources, createTaskResource, deleteTaskResource } from '../lib/api';

const App: React.FC = () => {
  const [session, setSession] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [newTaskName, setNewTaskName] = useState('');
  const [selectedTask, setSelectedTask] = useState<any>(null);
  
  const [resources, setResources] = useState<any[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newTitle, setNewTitle] = useState('');

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

  useEffect(() => {
    if (selectedTask) {
      loadResources(selectedTask.id);
      setShowAddForm(false);
      setNewUrl('');
      setNewTitle('');
    }
  }, [selectedTask]);

  const loadTasks = async () => {
    try {
      const data = await fetchApi('/api/tasks');
      setTasks(data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadResources = async (taskId: string) => {
    try {
      const data = await getTaskResources(taskId);
      setResources(data);
    } catch (e) {
      console.error(e);
    }
  };
  
  const handleSignOut = async () => {
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

  const handleAddResource = async () => {
    if (!newUrl) return;
    try {
      await createTaskResource(selectedTask.id, { url: newUrl, title: newTitle });
      setShowAddForm(false);
      setNewUrl('');
      setNewTitle('');
      loadResources(selectedTask.id);
    } catch (e: any) {
      console.error(e);
      alert('Failed to add resource: ' + e.message);
    }
  };

  const handleDeleteResource = async (resourceId: string) => {
    try {
      await deleteTaskResource(selectedTask.id, resourceId);
      loadResources(selectedTask.id);
    } catch (e) {
      console.error(e);
    }
  };

  const handleAddCurrentTab = async () => {
    if (!chrome || !chrome.tabs) {
      alert("Chrome tabs API not available");
      return;
    }
    
    try {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs && tabs.length > 0) {
          const activeTab = tabs[0];
          setNewUrl(activeTab.url || '');
          setNewTitle(activeTab.title || '');
          setShowAddForm(true);
        }
      });
    } catch (e) {
      console.error(e);
      alert("Failed to get current tab");
    }
  };

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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4>{resources.length} Resources</h4>
            <div>
              <button onClick={() => setShowAddForm(true)} style={{ marginRight: '5px' }}>+ Add Link</button>
              <button onClick={handleAddCurrentTab}>+ Add Current Tab</button>
            </div>
          </div>
          
          {showAddForm && (
            <div style={{ marginTop: '10px', padding: '10px', border: '1px solid #ccc', borderRadius: '4px' }}>
              <h5>Add Resource</h5>
              <div style={{ marginBottom: '5px' }}>
                <label style={{ display: 'block', fontSize: '12px' }}>URL:</label>
                <input type="text" value={newUrl} onChange={e => setNewUrl(e.target.value)} style={{ width: '100%' }} />
              </div>
              <div style={{ marginBottom: '10px' }}>
                <label style={{ display: 'block', fontSize: '12px' }}>Title:</label>
                <input type="text" value={newTitle} onChange={e => setNewTitle(e.target.value)} style={{ width: '100%' }} />
              </div>
              <button onClick={handleAddResource}>Save</button>
              <button onClick={() => setShowAddForm(false)} style={{ marginLeft: '5px' }}>Cancel</button>
            </div>
          )}
          
          {resources.length === 0 ? (
            <p>No resources yet.</p>
          ) : (
            <ul style={{ listStyleType: 'none', padding: 0 }}>
              {resources.map((res, idx) => (
                <li key={res.id} style={{ marginBottom: '10px', paddingBottom: '10px', borderBottom: '1px solid #eee' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div>
                      <strong>{idx + 1}. {res.title || 'Untitled'}</strong>
                      <br />
                      <a href={res.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '12px', color: '#3b82f6' }}>{res.url}</a>
                    </div>
                    <button onClick={() => handleDeleteResource(res.id)} style={{ alignSelf: 'flex-start' }}>Delete</button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
        
        <button className="delete-task-btn" onClick={(e) => handleDeleteTask(e, selectedTask.id)} style={{ marginTop: '20px' }}>Delete Task</button>
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
