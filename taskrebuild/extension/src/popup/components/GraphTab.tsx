import React, { useState, useEffect } from 'react';
import { getTaskGraph, analyzeTaskGraph, deleteGraphNode, deleteGraphEdge, rejectGraphEdge } from '../../lib/api';

interface GraphTabProps {
  taskId: string;
}

const GraphTab: React.FC<GraphTabProps> = ({ taskId }) => {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');

  const loadGraph = async () => {
    try {
      setError('');
      const data = await getTaskGraph(taskId);
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
    } catch (e: any) {
      console.error(e);
      setError('Failed to load graph data.');
    }
  };

  useEffect(() => {
    loadGraph();
  }, [taskId]);

  const handleAnalyzeGraph = async () => {
    setIsAnalyzing(true);
    setError('');
    try {
      await analyzeTaskGraph(taskId);
      await loadGraph();
    } catch (e: any) {
      console.error(e);
      setError('Graph analysis failed.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleRemoveNode = async (nodeId: string) => {
    try {
      await deleteGraphNode(taskId, nodeId);
      await loadGraph();
    } catch (e) {
      console.error(e);
    }
  };

  const handleRemoveEdge = async (edgeId: string) => {
    try {
      await deleteGraphEdge(taskId, edgeId);
      await loadGraph();
    } catch (e) {
      console.error(e);
    }
  };

  const handleRejectEdge = async (edgeId: string) => {
    try {
      await rejectGraphEdge(taskId, edgeId);
      await loadGraph();
    } catch (e) {
      console.error(e);
    }
  };

  // Basic representation
  const validEdges = edges.filter(e => !e.is_rejected);
  
  return (
    <div style={{ marginTop: '20px', padding: '15px', background: '#f8fafc', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h4 style={{ margin: 0, color: '#0f172a' }}>Knowledge Graph</h4>
        <button 
          onClick={handleAnalyzeGraph} 
          disabled={isAnalyzing}
          style={{ background: '#3b82f6', color: 'white', padding: '5px 10px', fontSize: '12px' }}
        >
          {isAnalyzing ? 'Analyzing...' : 'Analyze Task Graph'}
        </button>
      </div>
      
      {error && <p style={{ color: '#ef4444', fontSize: '12px', marginTop: '10px' }}>{error}</p>}
      
      <div style={{ marginTop: '15px' }}>
        {nodes.length === 0 ? (
          <p style={{ fontSize: '12px', color: '#64748b' }}>No graph data available. Run analysis to extract concepts.</p>
        ) : (
          <div>
            <h5 style={{ margin: '10px 0 5px 0', fontSize: '13px' }}>Nodes</h5>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {nodes.map(node => (
                <li key={node.id} style={{ marginBottom: '8px', padding: '8px', background: 'white', border: '1px solid #cbd5e1', borderRadius: '4px', fontSize: '12px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong>{node.label}</strong>
                    <button onClick={() => handleRemoveNode(node.id)} style={{ padding: '2px 5px', fontSize: '10px', background: 'transparent', color: '#ef4444', border: 'none' }}>Remove</button>
                  </div>
                  <div style={{ color: '#64748b', fontSize: '10px', display: 'flex', gap: '8px', marginTop: '4px' }}>
                    <span>Type: {node.node_type}</span>
                    {node.is_ai_generated && <span style={{ color: '#8b5cf6', fontWeight: 'bold' }}>AI inferred · {node.confidence?.toFixed(2) || '1.00'}</span>}
                  </div>
                  {node.description && <div style={{ marginTop: '4px', fontStyle: 'italic' }}>{node.description}</div>}
                </li>
              ))}
            </ul>

            <h5 style={{ margin: '15px 0 5px 0', fontSize: '13px' }}>Relationships</h5>
            {validEdges.length === 0 ? (
              <p style={{ fontSize: '12px', color: '#64748b' }}>No relationships extracted.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {validEdges.map(edge => {
                  const source = nodes.find(n => n.id === edge.source_node_id);
                  const target = nodes.find(n => n.id === edge.target_node_id);
                  return (
                    <li key={edge.id} style={{ marginBottom: '8px', padding: '8px', background: 'white', border: '1px solid #cbd5e1', borderRadius: '4px', fontSize: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <strong>{source ? source.label : 'Unknown'}</strong> 
                          <span style={{ margin: '0 8px', color: '#3b82f6' }}>── {edge.relationship_type} ──►</span> 
                          <strong>{target ? target.label : 'Unknown'}</strong>
                        </div>
                        <div style={{ display: 'flex', gap: '5px' }}>
                          <button onClick={() => handleRejectEdge(edge.id)} style={{ padding: '2px 5px', fontSize: '10px', background: '#fef2f2', color: '#ef4444', border: '1px solid #fca5a5' }}>Reject</button>
                          <button onClick={() => handleRemoveEdge(edge.id)} style={{ padding: '2px 5px', fontSize: '10px', background: 'transparent', color: '#64748b', border: 'none' }}>x</button>
                        </div>
                      </div>
                      <div style={{ color: '#64748b', fontSize: '10px', marginTop: '4px' }}>
                        {edge.is_ai_generated && <span style={{ color: '#8b5cf6', fontWeight: 'bold' }}>AI inferred · {edge.confidence?.toFixed(2) || '1.00'}</span>}
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GraphTab;
