import React, { useState, useEffect } from 'react';
import { getTaskResume, analyzeTaskResume, restoreWorkspace, getTaskResources } from '../../lib/api';

interface ResumeSectionProps {
  taskId: string;
}

const ResumeSection: React.FC<ResumeSectionProps> = ({ taskId }) => {
  const [resumeData, setResumeData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  
  // For modal
  const [availableResources, setAvailableResources] = useState<any[]>([]);
  const [selectedResourceIds, setSelectedResourceIds] = useState<Set<string>>(new Set());

  const [snapshots, setSnapshots] = useState<any[]>([]);
  const [showSnapshots, setShowSnapshots] = useState(false);

  const fetchResume = async () => {
    try {
      setLoading(true);
      const data = await getTaskResume(taskId);
      setResumeData(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleToggleSnapshots = async () => {
    if (!showSnapshots) {
      try {
        const { getTaskSnapshots } = await import('../../lib/api');
        const snaps = await getTaskSnapshots(taskId);
        setSnapshots(snaps || []);
      } catch (err) {
        console.error(err);
      }
    }
    setShowSnapshots(!showSnapshots);
  };

  useEffect(() => {
    fetchResume();
  }, [taskId]);

  const handleRefresh = async () => {
    try {
      setLoading(true);
      const data = await analyzeTaskResume(taskId);
      setResumeData(data);
    } catch (err: any) {
      console.error(err);
      alert('Error generating resume: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleOpenResumeModal = async () => {
    try {
      // Fetch all resources to let user pick
      const res = await getTaskResources(taskId);
      setAvailableResources(res || []);
      
      // Auto-select important ones if possible
      const importantIds = new Set<string>();
      if (resumeData?.state?.resume_analysis?.important_resources) {
         resumeData.state.resume_analysis.important_resources.forEach((r: any) => importantIds.add(r.resource_id));
      }
      setSelectedResourceIds(importantIds);
      
      setShowModal(true);
    } catch (err) {
      console.error(err);
      alert('Failed to load resources for restore.');
    }
  };

  const toggleResourceSelection = (id: string) => {
    const newSet = new Set(selectedResourceIds);
    if (newSet.has(id)) {
      newSet.delete(id);
    } else {
      newSet.add(id);
    }
    setSelectedResourceIds(newSet);
  };

  const handleRestoreSelected = async () => {
    if (selectedResourceIds.size === 0) {
      alert('Please select at least one resource to restore.');
      return;
    }
    try {
      const response = await restoreWorkspace(taskId, Array.from(selectedResourceIds));
      if (response && response.urls) {
        if (chrome && chrome.tabs) {
          response.urls.forEach((url: string) => {
             chrome.tabs.create({ url, active: false });
          });
        } else {
          alert('Cannot open tabs outside of extension environment. URLs: ' + response.urls.join(', '));
        }
      }
      setShowModal(false);
    } catch (err: any) {
      console.error(err);
      alert('Failed to restore workspace: ' + err.message);
    }
  };

  if (loading && !resumeData) return <div>Loading resume data...</div>;
  if (!resumeData && !loading) {
    return (
      <div style={{ marginBottom: '20px', padding: '10px', border: '1px solid #e5e7eb', borderRadius: '4px' }}>
        <h3 style={{ marginTop: 0 }}>WHERE YOU LEFT OFF</h3>
        <p>No resume data available yet.</p>
        <button onClick={handleRefresh}>Generate Resume</button>
      </div>
    );
  }

  const analysis = resumeData?.state?.resume_analysis;
  
  // Format date safely
  let lastActiveStr = "Unknown";
  if (resumeData?.created_at) {
     const date = new Date(resumeData.created_at);
     lastActiveStr = date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  }

  return (
    <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #e5e7eb', borderRadius: '8px', backgroundColor: '#f9fafb' }}>
      <h3 style={{ marginTop: 0, color: '#374151' }}>WHERE YOU LEFT OFF</h3>
      
      {loading && <p style={{ color: '#6b7280', fontStyle: 'italic' }}>Refreshing...</p>}
      
      {analysis && (
        <>
          <p style={{ fontWeight: '500', color: '#111827' }}>"{analysis.what_you_were_doing}"</p>
          <p style={{ fontSize: '12px', color: '#6b7280' }}>Last reconstructed: {lastActiveStr}</p>
          
          {analysis.important_resources && analysis.important_resources.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <strong style={{ fontSize: '13px' }}>Important resources:</strong>
              <ul style={{ margin: '5px 0', paddingLeft: '20px', fontSize: '13px' }}>
                {analysis.important_resources.map((r: any, idx: number) => (
                  <li key={idx}>{r.reason} (ID: {r.resource_id.substring(0,6)}...)</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.open_questions && analysis.open_questions.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <strong style={{ fontSize: '13px' }}>Open questions:</strong>
              <ul style={{ margin: '5px 0', paddingLeft: '20px', fontSize: '13px' }}>
                {analysis.open_questions.map((q: string, idx: number) => (
                  <li key={idx}>{q}</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.next_steps && analysis.next_steps.length > 0 && (
            <div style={{ marginTop: '10px' }}>
              <strong style={{ fontSize: '13px' }}>Suggested next steps:</strong>
              <ul style={{ margin: '5px 0', paddingLeft: '20px', fontSize: '13px' }}>
                {analysis.next_steps.map((s: string, idx: number) => (
                  <li key={idx}>{s}</li>
                ))}
              </ul>
            </div>
          )}
          
          <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
            <button onClick={handleOpenResumeModal} style={{ backgroundColor: '#2563eb', color: 'white', padding: '8px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>Resume Task</button>
            <button onClick={handleRefresh} style={{ backgroundColor: '#e5e7eb', color: '#374151', padding: '8px 12px', borderRadius: '4px', border: 'none', cursor: 'pointer' }}>Refresh Analysis</button>
            <button onClick={handleToggleSnapshots} style={{ backgroundColor: 'transparent', color: '#6b7280', padding: '8px 12px', borderRadius: '4px', border: '1px solid #d1d5db', cursor: 'pointer' }}>{showSnapshots ? 'Hide History' : 'Snapshot History'}</button>
          </div>
          
          <div style={{ marginTop: '10px', fontSize: '10px', color: '#9ca3af' }}>AI-generated</div>

          {showSnapshots && (
            <div style={{ marginTop: '20px', borderTop: '1px solid #e5e7eb', paddingTop: '10px' }}>
              <h4 style={{ margin: '0 0 10px 0' }}>Task Snapshots</h4>
              {snapshots.length === 0 ? <p style={{ fontSize: '12px', color: '#6b7280' }}>No snapshots yet.</p> : (
                <ul style={{ listStyleType: 'none', padding: 0, margin: 0 }}>
                  {snapshots.map(s => (
                    <li key={s.id} style={{ marginBottom: '10px', padding: '10px', backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '4px' }}>
                      <div style={{ fontSize: '11px', color: '#6b7280', marginBottom: '5px' }}>{new Date(s.created_at).toLocaleString()}</div>
                      <div style={{ fontSize: '13px' }}>{s.summary}</div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </>
      )}

      {/* Restore Modal */}
      {showModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', width: '90%', maxWidth: '400px', maxHeight: '80vh', overflowY: 'auto' }}>
            <h3 style={{ marginTop: 0 }}>Resume Task</h3>
            <p style={{ fontSize: '13px' }}>TaskRebuild found {availableResources.length} saved resources. The following tabs can be reopened:</p>
            
            <div style={{ marginBottom: '15px', border: '1px solid #e5e7eb', padding: '10px', borderRadius: '4px', maxHeight: '200px', overflowY: 'auto' }}>
              {availableResources.length === 0 ? (
                <p style={{ fontSize: '12px', color: '#6b7280' }}>No resources saved for this task.</p>
              ) : (
                availableResources.map(r => (
                  <div key={r.id} style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
                    <input 
                      type="checkbox" 
                      id={`res-${r.id}`} 
                      checked={selectedResourceIds.has(r.id)} 
                      onChange={() => toggleResourceSelection(r.id)} 
                    />
                    <label htmlFor={`res-${r.id}`} style={{ fontSize: '12px', marginLeft: '5px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {r.title || r.url}
                    </label>
                  </div>
                ))
              )}
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', color: '#6b7280' }}>{selectedResourceIds.size} resources selected</span>
              <div>
                <button onClick={() => setShowModal(false)} style={{ marginRight: '10px', background: 'none', border: '1px solid #d1d5db', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
                <button onClick={handleRestoreSelected} style={{ backgroundColor: '#2563eb', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>Restore Selected</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResumeSection;
