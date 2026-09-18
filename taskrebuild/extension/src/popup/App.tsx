import React, { useState, useEffect } from 'react';
import { fetchApi, getTaskResources, createTaskResource, deleteTaskResource, getTaskActivity } from '../lib/api';

const App: React.FC = () => {
  const [session, setSession] = useState<any>(null);
  const [tasks, setTasks] = useState<any[]>([]);
  const [newTaskName, setNewTaskName] = useState('');
  const [selectedTask, setSelectedTask] = useState<any>(null);
  
  const [resources, setResources] = useState<any[]>([]);
  const [activities, setActivities] = useState<any[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [newUrl, setNewUrl] = useState('');
  const [newTitle, setNewTitle] = useState('');

  // Phase 3 Active Task State
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [activeTaskName, setActiveTaskName] = useState<string | null>(null);

  useEffect(() => {
    // HARDCODED BYPASS FOR TESTING
    const dummySession = {
      access_token: 'PASTE_YOUR_USER_JWT_HERE',
      user: { id: 'c96c1bfb-3c54-4400-b162-22e2eb5d5220', email: 'mukesh.v@globalschoolsalumni.org' }
    };
    setSession(dummySession);
    localStorage.setItem('supabase-session', JSON.stringify(dummySession));
    
    // Also save for background script
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      chrome.storage.local.set({ 'supabase-session': JSON.stringify(dummySession) });
    }
    
    // Load local storage active task if any
    chrome.storage.local.get(['activeTaskId', 'activeTaskName'], (result) => {
      if (result.activeTaskId) {
        setActiveTaskId(result.activeTaskId);
        setActiveTaskName(result.activeTaskName);
      }
    });
    
    setTimeout(() => {
      loadTasks();
    }, 500);
  }, []);

  useEffect(() => {
    if (selectedTask) {
      loadResources(selectedTask.id);
      loadActivity(selectedTask.id);
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

  const loadActivity = async (taskId: string) => {
    try {
      const data = await getTaskActivity(taskId);
      setActivities(data);
    } catch (e) {
      console.error(e);
    }
  };
  
  const handleSignOut = async () => {
    setSession(null);
    chrome.storage.local.remove(['activeTaskId', 'activeTaskName']);
    setActiveTaskId(null);
    setActiveTaskName(null);
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
    e.stopPropagation(); 
    try {
      await fetchApi(`/api/tasks/${id}`, { method: 'DELETE' });
      if (selectedTask?.id === id) setSelectedTask(null);
      if (activeTaskId === id) {
        chrome.storage.local.remove(['activeTaskId', 'activeTaskName']);
        setActiveTaskId(null);
        setActiveTaskName(null);
      }
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

  const toggleTaskActive = (task: any) => {
    if (activeTaskId === task.id) {
      // Stop tracking
      chrome.storage.local.remove(['activeTaskId', 'activeTaskName']);
      setActiveTaskId(null);
      setActiveTaskName(null);
    } else {
      // Start tracking
      chrome.storage.local.set({ activeTaskId: task.id, activeTaskName: task.name });
      setActiveTaskId(task.id);
      setActiveTaskName(task.name);
    }
  };

  if (!session) return null;

  if (selectedTask) {
    const isActive = activeTaskId === selectedTask.id;
    return (
      <div className="popup-container">
        <button className="back-btn" onClick={() => setSelectedTask(null)}>← Back to tasks</button>
        <h2>📁 {selectedTask.name}</h2>
        <p style={{ fontSize: '12px', color: '#6b7280' }}>
          Created: {new Date(selectedTask.created_at).toLocaleDateString('en-US')}
        </p>
        
        <div style={{ marginBottom: '15px', padding: '10px', background: isActive ? '#ecfdf5' : '#f9fafb', borderRadius: '4px', border: isActive ? '1px solid #10b981' : '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <strong>Status: </strong> 
              {isActive ? (
                <span style={{ color: '#10b981' }}>● Active</span>
              ) : (
                <span style={{ color: '#6b7280' }}>Inactive</span>
              )}
            </div>
            <button 
              onClick={() => toggleTaskActive(selectedTask)}
              style={{ background: isActive ? '#ef4444' : '#10b981', color: 'white' }}
            >
              {isActive ? 'Stop Task' : 'Start Task'}
            </button>
          </div>
          <p style={{ fontSize: '11px', marginTop: '5px', color: '#6b7280' }}>
            {isActive 
              ? "TaskRebuild is recording browser tab activity for this active task." 
              : "Browser activity is not being recorded."}
          </p>
        </div>

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

        <div className="task-activity">
          <h4>Recent Activity ({activities.length})</h4>
          {activities.length === 0 ? (
            <p style={{ fontSize: '12px' }}>No recorded activity yet.</p>
          ) : (
            <ul style={{ listStyleType: 'none', padding: 0, maxHeight: '200px', overflowY: 'auto' }}>
              {activities.map((act) => (
                <li key={act.id} style={{ marginBottom: '5px', paddingBottom: '5px', borderBottom: '1px solid #eee', fontSize: '11px' }}>
                  <span style={{ background: '#e5e7eb', padding: '2px 4px', borderRadius: '3px', marginRight: '5px' }}>
                    {act.event_type}
                  </span>
                  {act.title ? <strong>{act.title}</strong> : act.url}
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
      
      <div style={{ padding: '10px', background: activeTaskId ? '#ecfdf5' : '#f9fafb', borderRadius: '4px', border: activeTaskId ? '1px solid #10b981' : '1px solid #e5e7eb', marginBottom: '15px' }}>
        <h4 style={{ margin: '0 0 5px 0' }}>Current Task</h4>
        {activeTaskId ? (
          <div>
            <span style={{ color: '#10b981', fontWeight: 'bold' }}>● {activeTaskName}</span>
            <p style={{ fontSize: '11px', margin: '5px 0 0 0', color: '#6b7280' }}>Recording browser tab activity.</p>
            <button onClick={() => toggleTaskActive({ id: activeTaskId })} style={{ marginTop: '10px', background: '#ef4444', color: 'white', fontSize: '12px' }}>Stop Task</button>
          </div>
        ) : (
          <div>
            <p style={{ margin: 0, fontSize: '12px' }}>No active task. Select a task to begin tracking.</p>
          </div>
        )}
      </div>
      
      <div className="tasks-section">
        <h3>My Tasks</h3>
        <ul className="task-list">
          {tasks.map(t => (
            <li key={t.id} onClick={() => setSelectedTask(t)} style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>
                📁 {t.name}
                {t.id === activeTaskId && <span style={{ marginLeft: '5px', color: '#10b981', fontSize: '10px' }}>●</span>}
              </span>
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
