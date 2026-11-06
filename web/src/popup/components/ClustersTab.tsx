import React, { useState, useEffect } from 'react';
import { fetchApi } from '../../lib/api';

interface ClustersTabProps {
  taskId: string;
}

const ClustersTab: React.FC<ClustersTabProps> = ({ taskId }) => {
  const [clusters, setClusters] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  const loadClusters = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchApi(`/api/tasks/${taskId}/clusters`);
      setClusters(data);
    } catch (e: any) {
      setError(e.message || 'Failed to load clusters');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    setError('');
    try {
      const res = await fetchApi(`/api/tasks/${taskId}/clusters/generate`, { method: 'POST' });
      if (res && res.clusters) {
        setClusters(res.clusters);
      } else {
        await loadClusters();
      }
    } catch (e: any) {
      setError(e.message || 'Failed to generate clusters');
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    loadClusters();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  return (
    <div style={{ marginTop: '16px', padding: '14px', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <h4 style={{ margin: 0, color: 'var(--accent-purple)' }}>🤖 AI Sub-task Clusters</h4>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button 
            onClick={loadClusters} 
            disabled={loading}
            style={{ background: 'var(--bg-subtle)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', padding: '4px 8px', fontSize: '11px', borderRadius: '4px' }}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button 
            onClick={handleGenerate} 
            disabled={generating}
            style={{ background: 'var(--accent-indigo)', color: '#ffffff', padding: '4px 10px', fontSize: '11px', borderRadius: '4px' }}
          >
            {generating ? 'Generating...' : 'Generate Clusters'}
          </button>
        </div>
      </div>

      {error && <p style={{ color: 'var(--accent-rose)', fontSize: '12px' }}>{error}</p>}

      {clusters.length === 0 && !loading && !error && (
        <p style={{ color: 'var(--text-muted)', fontSize: '12px' }}>No clusters found. Try generating them!</p>
      )}

      {clusters.map((cluster) => (
        <div key={cluster.id} style={{ marginBottom: '12px', padding: '12px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', background: 'var(--bg-primary)' }}>
          <h5 style={{ margin: '0 0 4px 0', fontSize: '13px', color: 'var(--text-primary)' }}>{cluster.label}</h5>
          <p style={{ margin: '0 0 8px 0', fontSize: '12px', color: 'var(--text-secondary)' }}>{cluster.summary}</p>
          <p style={{ margin: '0 0 8px 0', fontSize: '11px', color: 'var(--text-muted)', fontStyle: 'italic' }}><strong>Rationale:</strong> {cluster.rationale}</p>
          
          <h6 style={{ margin: '0 0 4px 0', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Sub-tasks ({cluster.members?.length || 0}):</h6>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '12px', color: 'var(--text-secondary)' }}>
            {cluster.members?.map((member: any) => (
              <li key={member.node_id}>{member.task_nodes?.label} <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>({member.task_nodes?.node_type})</span></li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default ClustersTab;
