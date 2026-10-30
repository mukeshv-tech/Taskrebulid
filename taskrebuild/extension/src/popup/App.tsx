import React, { useState, useEffect } from 'react';
import { fetchApi, getTaskResources, createTaskResource, deleteTaskResource, getTaskActivity, analyzeTask, getTaskAIAnalyses, deleteTaskActivity, deleteTaskAIAnalysis, clearTaskActivity } from '../lib/api';
import { supabase } from '../lib/supabase';
import GraphTab from './components/GraphTab';
import LearningPathTab from './components/LearningPathTab';
import SearchTab from './components/SearchTab';
import ResumeSection from './components/ResumeSection';
import ResourceMonitor from './components/ResourceMonitor';
import Auth from './components/Auth';
import ClustersTab from './components/ClustersTab';
import KnowledgeTab from './components/KnowledgeTab';

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
  
  // Phase 4 AI State
  const [aiAnalysis, setAiAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [aiError, setAiError] = useState('');

  // Phase 3 Active Task State
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [activeTaskName, setActiveTaskName] = useState<string | null>(null);

  const selectTask = (task: any) => {
    setSelectedTask(task);
    if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
      if (task && task.id) {
        chrome.storage.local.set({ selectedTaskId: task.id });
      } else {
        chrome.storage.local.remove(['selectedTaskId']);
      }
    }
  };

  useEffect(() => {
    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      handleSessionSetup(session);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      handleSessionSetup(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  const handleSessionSetup = (session: any) => {
    setSession(session);
    if (session) {
      if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
        chrome.storage.local.set({ 'supabase-session': JSON.stringify(session) });
      }
      
      chrome.storage.local.get(['activeTaskId', 'activeTaskName'], (result) => {
        if (result.activeTaskId) {
          setActiveTaskId(result.activeTaskId);
          setActiveTaskName(result.activeTaskName);
        }
      });
      setTimeout(() => {
        loadTasks();
      }, 500);
    } else {
      if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
        chrome.storage.local.remove('supabase-session');
      }
    }
  };

  useEffect(() => {
    if (selectedTask) {
      Promise.all([
        loadResources(selectedTask.id),
        loadActivity(selectedTask.id),
        loadAiAnalyses(selectedTask.id)
      ]);
      setShowAddForm(false);
      setNewUrl('');
      setNewTitle('');
    }
  }, [selectedTask]);

  const loadAiAnalyses = async (taskId: string) => {
    try {
      setAiError('');
      const analyses = await getTaskAIAnalyses(taskId);
      if (analyses && analyses.length > 0) {
        const match = analyses.find((a: any) => 
          a.analysis_type === 'full_task_analysis' || 
          (a.result && (a.result.task_summary !== undefined || a.result.topics !== undefined))
        ) || analyses[0];

        if (match && match.result && !match.result.markdown) {
          setAiAnalysis(match);
        } else {
          setAiAnalysis(null);
        }
      } else {
        setAiAnalysis(null);
      }
    } catch (e: any) {
      console.error(e);
      setAiError(e.message || 'Failed to load AI analysis');
    }
  };

  const loadTasks = async () => {
    try {
      const data = await fetchApi('/api/tasks');
      setTasks(data);

      if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
        chrome.storage.local.set({ cachedTasks: data });
        chrome.storage.local.get(['selectedTaskId'], (result) => {
          if (result && result.selectedTaskId && data && data.length > 0) {
            const found = data.find((t: any) => t.id === result.selectedTaskId);
            if (found) {
              setSelectedTask(found);
            }
          }
        });
      }
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
    await supabase.auth.signOut();
    setSession(null);
    chrome.storage.local.remove(['activeTaskId', 'activeTaskName', 'selectedTaskId']);
    setActiveTaskId(null);
    setActiveTaskName(null);
    setSelectedTask(null);
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
      if (selectedTask?.id === id) selectTask(null);
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

  const handleAnalyzeTask = async () => {
    if (!selectedTask || isAnalyzing) return;
    setIsAnalyzing(true);
    setAiError('');
    try {
      if (aiAnalysis) {
        await deleteTaskAIAnalysis(selectedTask.id);
        setAiAnalysis(null);
      }
      const result = await analyzeTask(selectedTask.id);
      setAiAnalysis(result);
    } catch (e: any) {
      console.error(e);
      setAiError(e.message || 'AI analysis is temporarily unavailable.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleDeleteActivity = async (activityId: string) => {
    try {
      await deleteTaskActivity(selectedTask.id, activityId);
      loadActivity(selectedTask.id);
    } catch (e) {
      console.error(e);
    }
  };

  const handleClearAllActivity = async () => {
    if (window.confirm("Are you sure you want to clear all activity for this task?")) {
      try {
        await clearTaskActivity(selectedTask.id);
        loadActivity(selectedTask.id);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleDeleteAnalysis = async () => {
    try {
      await deleteTaskAIAnalysis(selectedTask.id);
      setAiAnalysis(null);
      loadAiAnalyses(selectedTask.id);
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

  if (!session) return <Auth onSession={handleSessionSetup} />;

  if (selectedTask) {
    const isActive = activeTaskId === selectedTask.id;
    return (
      <div className="popup-container">
        <button className="back-btn" onClick={() => selectTask(null)}>← Back to tasks</button>
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

        <ResumeSection taskId={selectedTask.id} />
        
        <ResourceMonitor taskId={selectedTask.id} />

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
                      <a href={res.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '12px', color: '#3b82f6', wordBreak: 'break-all' }}>{res.url}</a>
                    </div>
                    <button onClick={() => handleDeleteResource(res.id)} style={{ alignSelf: 'flex-start' }}>Delete</button>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="task-activity">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <h4 style={{ margin: 0 }}>Recent Activity ({activities.length})</h4>
            {activities.length > 0 && (
              <button onClick={handleClearAllActivity} style={{ fontSize: '10px', padding: '2px 5px', color: '#ef4444', background: 'transparent', border: '1px solid #ef4444' }}>Clear All</button>
            )}
          </div>
          {activities.length === 0 ? (
            <p style={{ fontSize: '12px' }}>No recorded activity yet.</p>
          ) : (
            <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {Object.entries(activities.reduce((acc, act) => {
                const date = new Date(act.timestamp).toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' });
                if (!acc[date]) acc[date] = [];
                acc[date].push(act);
                return acc;
              }, {} as Record<string, any[]>)).map(([dateStr, acts]) => (
                <div key={dateStr} style={{ marginBottom: '10px' }}>
                  <div style={{ fontWeight: 'bold', fontSize: '12px', borderBottom: '1px solid #ccc', marginBottom: '5px' }}>{dateStr}</div>
                  <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                    {(acts as any[]).map((act: any) => (
                      <li key={act.id} style={{ marginBottom: '5px', paddingBottom: '5px', borderBottom: '1px solid #eee', fontSize: '11px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <span style={{ background: '#e5e7eb', padding: '2px 4px', borderRadius: '3px', marginRight: '5px' }}>
                            {String(act.event_type)}
                          </span>
                          {act.title ? <strong>{String(act.title)}</strong> : <span style={{ wordBreak: 'break-all' }}>{act.url}</span>}
                        </div>
                        <button onClick={() => handleDeleteActivity(act.id)} style={{ padding: '2px 5px', fontSize: '10px' }}>x</button>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="task-ai-analysis" style={{ marginTop: '20px', padding: '15px', background: '#f5f3ff', borderRadius: '4px', border: '1px solid #ddd6fe' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h4 style={{ margin: 0, color: '#4c1d95' }}>AI Analysis</h4>
            <div style={{ display: 'flex', gap: '10px' }}>
                <button 
                  onClick={handleAnalyzeTask} 
                  disabled={isAnalyzing}
                  style={{ background: '#8b5cf6', color: 'white' }}
                >
                  {aiAnalysis ? (isAnalyzing ? 'Refreshing...' : 'Refresh Analysis') : (isAnalyzing ? 'Analyzing...' : 'Analyze Task')}
                </button>
            </div>
          </div>
          
          {aiError && <p style={{ color: '#ef4444', fontSize: '12px', marginTop: '10px' }}>{aiError}</p>}
          
          {aiAnalysis && aiAnalysis.result && (
            <div style={{ marginTop: '15px', fontSize: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ background: '#ddd6fe', color: '#4c1d95', padding: '2px 6px', borderRadius: '10px', fontSize: '10px', fontWeight: 'bold' }}>AI-generated</span>
                <button onClick={(e) => { e.preventDefault(); e.stopPropagation(); handleDeleteAnalysis(); }} style={{ padding: '2px 5px', fontSize: '10px', background: 'transparent', color: '#ef4444', border: '1px solid #ef4444', borderRadius: '3px', cursor: 'pointer' }}>Delete Analysis</button>
              </div>
              
              {aiAnalysis.result.task_summary ? (
                <p style={{ fontStyle: 'italic', marginTop: '10px', color: '#374151', lineHeight: '1.4' }}>"{aiAnalysis.result.task_summary}"</p>
              ) : (
                <p style={{ fontStyle: 'italic', marginTop: '10px', color: '#9ca3af' }}>No summary generated yet. Click "Refresh Analysis" to analyze this task.</p>
              )}
              
              <h5 style={{ margin: '12px 0 5px 0', color: '#1f2937' }}>Topics</h5>
              {(!aiAnalysis.result.topics || aiAnalysis.result.topics.length === 0) ? (
                <p style={{ color: '#9ca3af', fontSize: '11px', margin: '0 0 10px 0' }}>No topics extracted yet. Click Refresh Analysis to identify topics.</p>
              ) : (
                <ul style={{ margin: '0 0 10px 0', paddingLeft: '20px' }}>
                  {aiAnalysis.result.topics.map((t: any, i: number) => (
                    <li key={i}>{String(t.name)} {t.confidence !== undefined && <span style={{ color: '#6b7280', fontSize: '10px' }}>({Math.round((t.confidence || 1) * 100)}%)</span>}</li>
                  ))}
                </ul>
              )}
              
              <h5 style={{ margin: '12px 0 5px 0', color: '#1f2937' }}>Resource Analysis</h5>
              {(!aiAnalysis.result.resource_analysis || aiAnalysis.result.resource_analysis.length === 0) ? (
                <p style={{ color: '#9ca3af', fontSize: '11px', margin: '0 0 10px 0' }}>No resources analyzed yet. Add current tabs or links above to get relevance insights.</p>
              ) : (
                <ul style={{ margin: '0 0 10px 0', paddingLeft: '20px' }}>
                  {aiAnalysis.result.resource_analysis.map((r: any, i: number) => {
                    const res = resources.find(rx => rx.id === r.resource_id);
                    return (
                      <li key={i}>
                        <strong>{String(res ? res.title || res.url : r.resource_id)}</strong> - Relevance: {String(r.relevance)}
                        <br/>
                        <span style={{ color: '#6b7280' }}>{String(r.reason)}</span>
                      </li>
                    );
                  })}
                </ul>
              )}
              
              <h5 style={{ margin: '12px 0 5px 0', color: '#1f2937' }}>Suggested Next Steps</h5>
              {(!aiAnalysis.result.suggested_next_steps || aiAnalysis.result.suggested_next_steps.length === 0) ? (
                <p style={{ color: '#9ca3af', fontSize: '11px', margin: '0 0 10px 0' }}>No next steps available yet.</p>
              ) : (
                <ul style={{ margin: '0 0 10px 0', paddingLeft: '20px' }}>
                  {aiAnalysis.result.suggested_next_steps.map((step: string, i: number) => (
                    <li key={i}>{String(step)}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>
        
        <SearchTab taskId={selectedTask.id} />
        <GraphTab taskId={selectedTask.id} />
        <ClustersTab taskId={selectedTask.id} />
        <LearningPathTab taskId={selectedTask.id} />
        <KnowledgeTab taskId={selectedTask.id} taskName={selectedTask.name} />

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
      
      <SearchTab onNavigateToTask={(tid) => {
        const t = tasks.find(x => x.id === tid);
        if (t) selectTask(t);
      }} />
      
      <KnowledgeTab />

      <div className="tasks-section">
        <h3>My Tasks</h3>
        <ul className="task-list">
          {tasks.map(t => (
            <li key={t.id} onClick={() => selectTask(t)} style={{ cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
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
