import React, { useState, useEffect, useCallback } from 'react';
import { getTaskGraph, analyzeTaskGraph, getClusters, generateClusters } from '../../lib/api';
import { ReactFlow, Controls, Background, MarkerType, applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface GraphTabProps {
  taskId: string;
}

const CLUSTER_COLORS = [
  '#f59e0b', // amber
  '#10b981', // emerald
  '#3b82f6', // blue
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
];

const GraphTab: React.FC<GraphTabProps> = ({ taskId }) => {
  const [rawNodes, setRawNodes] = useState<any[]>([]);
  const [rawEdges, setRawEdges] = useState<any[]>([]);
  const [clusters, setClusters] = useState<any[]>([]);
  
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isClustering, setIsClustering] = useState(false);
  const [error, setError] = useState('');
  
  const [colorByCluster, setColorByCluster] = useState(false);

  const loadGraph = async () => {
    try {
      setError('');
      const data = await getTaskGraph(taskId);
      setRawNodes(data.nodes || []);
      setRawEdges(data.edges || []);
      
      const clusterData = await getClusters(taskId);
      setClusters(clusterData.clusters || []);
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

  const handleClusterGraph = async () => {
    setIsClustering(true);
    setError('');
    try {
      const res = await generateClusters(taskId);
      setClusters(res.clusters || []);
      setColorByCluster(true);
    } catch (e: any) {
      console.error(e);
      setError('Clustering failed.');
    } finally {
      setIsClustering(false);
    }
  };

  // Process data into React Flow format
  useEffect(() => {
    if (rawNodes.length === 0) return;

    // Filter rejected edges
    const validRawEdges = rawEdges.filter(e => !e.is_rejected);
    
    // Simple Circular Layout
    const centerX = 200;
    const centerY = 150;
    const radius = 120;
    const angleStep = (2 * Math.PI) / (rawNodes.length - 1 || 1);
    
    let currentAngle = 0;

    const flowNodes = rawNodes.map((n) => {
      let bg = '#334155'; // default slate
      let border = '#94a3b8';
      
      // Node type coloring
      if (n.node_type === 'task') { bg = '#5b21b6'; border = '#8b5cf6'; }
      else if (n.node_type === 'resource') { bg = '#1e3a8a'; border = '#3b82f6'; }
      else if (n.node_type === 'activity') { bg = '#064e3b'; border = '#10b981'; }
      else if (n.node_type === 'concept') { bg = '#831843'; border = '#f43f5e'; }

      // Cluster coloring override
      if (colorByCluster && clusters.length > 0) {
        const cIndex = clusters.findIndex(c => c.node_ids.includes(n.id));
        if (cIndex !== -1) {
          bg = '#1e1e1e';
          border = CLUSTER_COLORS[cIndex % CLUSTER_COLORS.length];
        }
      }

      let x = centerX;
      let y = centerY;
      if (n.node_type !== 'task') {
        x = centerX + radius * Math.cos(currentAngle);
        y = centerY + radius * Math.sin(currentAngle);
        currentAngle += angleStep;
      }

      return {
        id: n.id,
        position: { x, y },
        data: { label: n.label },
        style: {
          background: bg,
          color: '#f8fafc',
          border: `2px solid ${border}`,
          borderRadius: '6px',
          padding: '8px',
          fontSize: '10px',
          width: 120,
          boxShadow: `0 0 10px ${border}40`,
        },
      };
    });

    const flowEdges = validRawEdges.map(e => ({
      id: e.id,
      source: e.source_node_id,
      target: e.target_node_id,
      label: e.relationship_type,
      labelStyle: { fill: '#94a3b8', fontSize: 9 },
      labelBgStyle: { fill: '#1e1e1e', fillOpacity: 0.8 },
      style: { stroke: '#475569', strokeWidth: 1.5 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#475569',
      },
    }));
    
    const safeEdges = flowEdges.filter(e => 
      flowNodes.find(n => n.id === e.source) && flowNodes.find(n => n.id === e.target)
    );

    setNodes(flowNodes);
    setEdges(safeEdges);
  }, [rawNodes, rawEdges, clusters, colorByCluster]);

  const onNodesChange = useCallback((changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);

  return (
    <div style={{ marginTop: '20px', background: '#121212', borderRadius: '8px', border: '1px solid #333', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 15px', borderBottom: '1px solid #333', background: '#1e1e1e' }}>
        <h4 style={{ margin: 0, color: '#e5e7eb', fontSize: '13px' }}>🧠 Obsidian Map</h4>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button 
            onClick={handleClusterGraph} 
            disabled={isClustering || rawNodes.length === 0}
            style={{ background: '#0f766e', color: 'white', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer', opacity: isClustering ? 0.7 : 1 }}
          >
            {isClustering ? 'Clustering...' : 'Auto-Cluster'}
          </button>
          <button 
            onClick={handleAnalyzeGraph} 
            disabled={isAnalyzing}
            style={{ background: '#8b5cf6', color: 'white', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer', opacity: isAnalyzing ? 0.7 : 1 }}
          >
            {isAnalyzing ? 'Analyzing...' : 'Generate Connections'}
          </button>
        </div>
      </div>
      
      {error && <p style={{ color: '#ef4444', fontSize: '12px', padding: '0 15px' }}>{error}</p>}
      
      <div style={{ width: '100%', height: '350px', position: 'relative' }}>
        {rawNodes.length === 0 ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#6b7280', fontSize: '12px' }}>
            No graph data. Click Generate Connections.
          </div>
        ) : (
          <ReactFlow 
            nodes={nodes} 
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            attributionPosition="bottom-right"
          >
            <Background color="#333" gap={16} />
            <Controls style={{ fill: '#fff', background: '#252525' }} />
          </ReactFlow>
        )}
      </div>
      
      {clusters.length > 0 && (
        <div style={{ padding: '10px 15px', background: '#1e1e1e', borderTop: '1px solid #333' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <h5 style={{ margin: 0, color: '#e2e8f0', fontSize: '12px' }}>AI Sub-Task Clusters</h5>
            <label style={{ fontSize: '11px', color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '5px', cursor: 'pointer' }}>
              <input type="checkbox" checked={colorByCluster} onChange={(e) => setColorByCluster(e.target.checked)} />
              Color nodes by cluster
            </label>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '150px', overflowY: 'auto' }}>
            {clusters.map((c, i) => (
              <div key={i} style={{ borderLeft: `3px solid ${CLUSTER_COLORS[i % CLUSTER_COLORS.length]}`, paddingLeft: '8px' }}>
                <strong style={{ color: '#f8fafc', fontSize: '11px' }}>{c.cluster_name}</strong>
                <p style={{ margin: '2px 0 0 0', color: '#94a3b8', fontSize: '10px' }}>{c.summary}</p>
                <div style={{ marginTop: '2px', color: '#64748b', fontSize: '9px' }}>
                  {c.node_ids.length} nodes assigned
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphTab;
