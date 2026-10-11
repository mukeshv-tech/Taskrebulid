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
  }, [taskId]);

  return (
    <div style={{ padding: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h4 style={{ margin: 0, color: '#4c1d95' }}>AI Sub-task Clusters</h4>
        <div>
          <button 
            onClick={loadClusters} 
            disabled={loading}
            style={{ marginRight: '10px', background: 'transparent', border: '1px solid #ccc' }}
          >
            {loading ? 'Refreshing...' : 'Refresh'}
          </button>
          <button 
            onClick={handleGenerate} 
            disabled={generating}
            style={{ background: '#8b5cf6', color: 'white' }}
          >
            {generating ? 'Generating...' : 'Generate New Clusters'}
          </button>
        </div>
      </div>

      {error && <p style={{ color: '#ef4444', fontSize: '12px' }}>{error}</p>}

      {clusters.length === 0 && !loading && !error && (
        <p style={{ color: '#666', fontSize: '12px' }}>No clusters found. Try generating them!</p>
      )}

      {clusters.map((cluster) => (
        <div key={cluster.id} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #e5e7eb', borderRadius: '6px', background: '#fff' }}>
          <h5 style={{ margin: '0 0 5px 0', fontSize: '14px', color: '#111827' }}>{cluster.label}</h5>
          <p style={{ margin: '0 0 10px 0', fontSize: '12px', color: '#4b5563' }}>{cluster.summary}</p>
          <p style={{ margin: '0 0 10px 0', fontSize: '11px', color: '#6b7280', fontStyle: 'italic' }}><strong>Rationale:</strong> {cluster.rationale}</p>
          
          <h6 style={{ margin: '0 0 5px 0', fontSize: '11px', color: '#374151', textTransform: 'uppercase' }}>Sub-tasks ({cluster.members?.length || 0}):</h6>
          <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '12px' }}>
            {cluster.members?.map((member: any) => (
              <li key={member.node_id}>{member.task_nodes?.label} <span style={{ color: '#9ca3af', fontSize: '10px' }}>({member.task_nodes?.node_type})</span></li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default ClustersTab;
