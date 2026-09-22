import React, { useState, useEffect } from 'react';
import { getTaskResourcesStatus, triggerResourceCheck, analyzeResourceReplacement, replaceResourceWithExisting } from '../../lib/api';

interface ResourceMonitorProps {
  taskId: string;
}

const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ taskId }) => {
  const [resources, setResources] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [checkingId, setCheckingId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Replacement analysis
  const [analyzingId, setAnalyzingId] = useState<string | null>(null);
  const [candidatesMap, setCandidatesMap] = useState<Record<string, any[]>>({});
  const [showReplaceModal, setShowReplaceModal] = useState<string | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<string | null>(null);

  const fetchResources = async () => {
    try {
      setLoading(true);
      const data = await getTaskResourcesStatus(taskId);
      setResources(data || []);
    } catch (err: any) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResources();
  }, [taskId]);

  const handleCheckNow = async (resourceId: string) => {
    try {
      setCheckingId(resourceId);
      await triggerResourceCheck(taskId, resourceId);
      await fetchResources();
    } catch (err: any) {
      console.error(err);
      alert('Check failed: ' + err.message);
    } finally {
      setCheckingId(null);
    }
  };

  const handleFindAlternatives = async (resourceId: string) => {
    try {
      setAnalyzingId(resourceId);
      const result = await analyzeResourceReplacement(taskId, resourceId);
      if (result && result.candidates) {
        setCandidatesMap(prev => ({ ...prev, [resourceId]: result.candidates }));
      }
    } catch (err: any) {
      console.error(err);
      alert('Analysis failed: ' + err.message);
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleOpenReplace = (resourceId: string) => {
    setShowReplaceModal(resourceId);
    setSelectedCandidate(null);
  };

  const handleConfirmReplace = async () => {
    if (!showReplaceModal || !selectedCandidate) return;
    try {
      await replaceResourceWithExisting(taskId, showReplaceModal, selectedCandidate);
      setShowReplaceModal(null);
      await fetchResources();
    } catch (err: any) {
      console.error(err);
      alert('Replacement failed: ' + err.message);
    }
  };

  const getStatusDisplay = (r: any) => {
    if (r.replaced_by_resource_id) return <span style={{ color: '#6b7280' }}>Replaced</span>;
    if (!r.check_status) return <span style={{ color: '#6b7280' }}>Never checked</span>;
    
    switch (r.check_status) {
      case 'available':
        if (r.change_type === 'redirected') return <span style={{ color: '#d97706' }}>↪ Redirected</span>;
        if (r.change_type === 'title_changed' || r.change_type === 'content_changed') return <span style={{ color: '#2563eb' }}>Changed</span>;
        return <span style={{ color: '#16a34a' }}>✓ Available</span>;
      case 'not_found':
      case 'forbidden':
      case 'server_error':
      case 'timeout':
      case 'network_error':
      case 'invalid_url':
        return <span style={{ color: '#ef4444' }}>⚠ Resource unavailable ({r.check_status})</span>;
      default:
        return <span style={{ color: '#6b7280' }}>{r.check_status}</span>;
    }
  };

  const needsAttention = (r: any) => {
    return !r.replaced_by_resource_id && r.check_status && r.check_status !== 'available';
  };

  const activeResources = resources.filter(r => !r.replaced_by_resource_id);

  if (activeResources.length === 0 && !loading) {
    return null;
  }

  return (
    <div style={{ marginBottom: '20px', padding: '15px', border: '1px solid #e5e7eb', borderRadius: '8px', backgroundColor: '#fff' }}>
      <h3 style={{ marginTop: 0, color: '#111827' }}>RESOURCE ALERTS</h3>
      {error && <p style={{ color: 'red', fontSize: '12px' }}>{error}</p>}
      
      {loading && resources.length === 0 && <p style={{ fontSize: '12px', color: '#6b7280' }}>Loading resources...</p>}
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
        {activeResources.map(r => (
          <div key={r.id} style={{ border: '1px solid #f3f4f6', padding: '10px', borderRadius: '4px', backgroundColor: needsAttention(r) ? '#fef2f2' : '#f9fafb' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontWeight: '500', fontSize: '13px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.title || r.url}</div>
                <a href={r.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '11px', color: '#6b7280', textDecoration: 'none', display: 'block', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{r.url}</a>
              </div>
              <button 
                onClick={() => handleCheckNow(r.id)} 
                disabled={checkingId === r.id}
                style={{ height: '24px', fontSize: '10px', padding: '0 8px', background: 'white', border: '1px solid #d1d5db', borderRadius: '4px', cursor: 'pointer', flexShrink: 0, marginLeft: '10px' }}
              >
                {checkingId === r.id ? 'Checking...' : 'Check Now'}
              </button>
            </div>
            
            <div style={{ marginTop: '8px', fontSize: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <strong>Status:</strong> {getStatusDisplay(r)}
                {r.last_checked_at && <span style={{ marginLeft: '10px', color: '#9ca3af' }}>Last checked: {new Date(r.last_checked_at).toLocaleDateString()}</span>}
              </div>
            </div>

            {needsAttention(r) && (
              <div style={{ marginTop: '10px', borderTop: '1px solid #fecaca', paddingTop: '10px' }}>
                <p style={{ margin: '0 0 10px 0', fontSize: '12px', color: '#991b1b' }}>This resource appears unavailable.</p>
                <button 
                  onClick={() => handleFindAlternatives(r.id)} 
                  disabled={analyzingId === r.id}
                  style={{ fontSize: '11px', padding: '4px 8px', background: 'white', border: '1px solid #d1d5db', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}
                >
                  {analyzingId === r.id ? 'Analyzing...' : 'Find Alternatives'}
                </button>
                <button 
                  onClick={() => handleOpenReplace(r.id)}
                  style={{ fontSize: '11px', padding: '4px 8px', background: '#2563eb', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
                >
                  Replace
                </button>

                {candidatesMap[r.id] && (
                  <div style={{ marginTop: '10px', backgroundColor: 'white', padding: '10px', borderRadius: '4px', border: '1px solid #e5e7eb' }}>
                    <h5 style={{ margin: '0 0 5px 0' }}>Possible alternatives:</h5>
                    {candidatesMap[r.id].length === 0 ? (
                      <p style={{ fontSize: '11px', color: '#6b7280', margin: 0 }}>No suitable candidates found.</p>
                    ) : (
                      <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '11px' }}>
                        {candidatesMap[r.id].map((cand: any, idx: number) => {
                          const candRes = resources.find(res => res.id === cand.resource_id);
                          return (
                            <li key={idx} style={{ marginBottom: '5px' }}>
                              <strong>{candRes?.title || cand.resource_id}</strong> (Confidence: {cand.confidence})
                              <br /><span style={{ color: '#6b7280' }}>{cand.reason}</span>
                            </li>
                          );
                        })}
                      </ul>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {showReplaceModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000 }}>
          <div style={{ background: 'white', padding: '20px', borderRadius: '8px', width: '90%', maxWidth: '400px' }}>
            <h3 style={{ marginTop: 0 }}>Replace Resource</h3>
            <p style={{ fontSize: '12px' }}>Select an existing resource to replace the unavailable one.</p>
            
            <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #e5e7eb', padding: '10px', marginBottom: '15px' }}>
              {resources.filter(res => res.id !== showReplaceModal && !res.replaced_by_resource_id).map(res => (
                <div key={res.id} style={{ marginBottom: '5px' }}>
                  <label style={{ fontSize: '12px', display: 'flex', alignItems: 'center' }}>
                    <input 
                      type="radio" 
                      name="replacementCandidate" 
                      value={res.id} 
                      checked={selectedCandidate === res.id}
                      onChange={() => setSelectedCandidate(res.id)}
                      style={{ marginRight: '8px' }}
                    />
                    <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                      {res.title || res.url}
                    </div>
                  </label>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
              <button onClick={() => setShowReplaceModal(null)} style={{ background: 'white', border: '1px solid #d1d5db', padding: '6px 12px', borderRadius: '4px', cursor: 'pointer' }}>Cancel</button>
              <button onClick={handleConfirmReplace} disabled={!selectedCandidate} style={{ background: '#2563eb', color: 'white', border: 'none', padding: '6px 12px', borderRadius: '4px', cursor: selectedCandidate ? 'pointer' : 'not-allowed' }}>Confirm Replacement</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResourceMonitor;
