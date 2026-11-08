import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  getTaskGraph,
  analyzeTaskGraph,
  getClusters,
  generateClusters,
  deleteGraphNode,
  deleteGraphEdge,
  rejectGraphEdge
} from '../../lib/api';
import { ReactFlow, Controls, Background, MarkerType, applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { GalaxyGraph, GalaxyNode } from './GalaxyGraph';

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
  const [successMsg, setSuccessMsg] = useState('');
  
  const [colorByCluster, setColorByCluster] = useState(false);
  const [viewMode, setViewMode] = useState<'galaxy' | 'flow'>('galaxy');

  // Search & Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const loadGraph = async () => {
    try {
      setError('');
      const data = await getTaskGraph(taskId);
      setRawNodes(data.nodes || []);
      setRawEdges(data.edges || []);
      
      const clusterData = await getClusters(taskId);
      const list = Array.isArray(clusterData) ? clusterData : (clusterData?.clusters || []);
      setClusters(list);
    } catch (e: any) {
      console.error(e);
      setError('Failed to load graph data.');
    }
  };

  useEffect(() => {
    loadGraph();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [taskId]);

  const handleAnalyzeGraph = async () => {
    setIsAnalyzing(true);
    setError('');
    setSuccessMsg('');
    try {
      await analyzeTaskGraph(taskId);
      await loadGraph();
      setSuccessMsg('Graph generated with AI connections!');
      setTimeout(() => setSuccessMsg(''), 4000);
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
      const list = Array.isArray(res) ? res : (res?.clusters || []);
      setClusters(list);
      setColorByCluster(true);
    } catch (e: any) {
      console.error(e);
      setError(e.message || 'Clustering failed.');
    } finally {
      setIsClustering(false);
    }
  };

  const handleDeleteNode = async (nodeId: string) => {
    if (!confirm('Are you sure you want to delete this node from the graph?')) return;
    try {
      await deleteGraphNode(taskId, nodeId);
      setSelectedNodeId(null);
      await loadGraph();
    } catch (e: any) {
      console.error(e);
      setError('Failed to delete node.');
    }
  };

  const handleDeleteEdge = async (edgeId: string) => {
    try {
      await deleteGraphEdge(taskId, edgeId);
      await loadGraph();
    } catch (e: any) {
      console.error(e);
      setError('Failed to delete relationship.');
    }
  };

  const handleRejectEdge = async (edgeId: string) => {
    try {
      await rejectGraphEdge(taskId, edgeId);
      await loadGraph();
    } catch (e: any) {
      console.error(e);
      setError('Failed to reject relationship.');
    }
  };

  // Process data into React Flow format
  useEffect(() => {
    if (rawNodes.length === 0) return;

    const validRawEdges = rawEdges.filter(e => !e.is_rejected);
    
    const centerX = 200;
    const centerY = 150;
    const radius = 120;
    const angleStep = (2 * Math.PI) / (rawNodes.length - 1 || 1);
    
    let currentAngle = 0;

    const flowNodes = rawNodes.map((n) => {
      let x = centerX;
      let y = centerY;
      
      if (n.node_type !== 'task') {
        x = centerX + radius * Math.cos(currentAngle);
        y = centerY + radius * Math.sin(currentAngle);
        currentAngle += angleStep;
      }

      let bg = '#1e1e1e';
      let border = '#3b82f6';

      if (colorByCluster && clusters.length > 0) {
        const cIndex = clusters.findIndex(c => {
          const ids = c.node_ids || c.members?.map((m: any) => m.node_id) || [];
          return ids.includes(n.id);
        });
        if (cIndex !== -1) {
          border = CLUSTER_COLORS[cIndex % CLUSTER_COLORS.length];
        }
      } else {
        if (n.node_type === 'task') border = '#8b5cf6';
        if (n.node_type === 'resource') border = '#3b82f6';
        if (n.node_type === 'activity') border = '#10b981';
        if (n.node_type === 'concept') border = '#ec4899';
      }

      return {
        id: n.id,
        data: { label: n.label },
        position: { x, y },
        style: {
          background: bg,
          color: '#fff',
          border: `2px solid ${border}`,
          borderRadius: n.node_type === 'task' ? '20px' : '8px',
          padding: '6px 10px',
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

  const nodeStats = useMemo(() => {
    const types: Record<string, number> = {};
    for (const n of rawNodes) {
      const t = n.node_type || 'concept';
      types[t] = (types[t] || 0) + 1;
    }
    return types;
  }, [rawNodes]);

  return (
    <div style={{ marginTop: '20px', background: '#121212', borderRadius: '8px', border: '1px solid #333', overflow: 'hidden' }}>
      {/* Header bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 14px', borderBottom: '1px solid #333', background: '#1e1e1e' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <h4 style={{ margin: 0, color: '#e5e7eb', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>🪐</span> Knowledge Map
          </h4>
          <span style={{ fontSize: '10px', color: '#94a3b8', background: '#262626', padding: '2px 6px', borderRadius: '4px' }}>
            {rawNodes.length} nodes · {rawEdges.filter(e => !e.is_rejected).length} links
          </span>
        </div>

        <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
          {/* Galaxy vs 2D Flow Toggle */}
          <div style={{ display: 'flex', background: '#262626', borderRadius: '4px', padding: '2px' }}>
            <button
              onClick={() => setViewMode('galaxy')}
              style={{
                background: viewMode === 'galaxy' ? '#38bdf8' : 'none',
                color: viewMode === 'galaxy' ? '#0f172a' : '#94a3b8',
                border: 'none',
                borderRadius: '3px',
                padding: '2px 7px',
                fontSize: '10px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              Galaxy
            </button>
            <button
              onClick={() => setViewMode('flow')}
              style={{
                background: viewMode === 'flow' ? '#38bdf8' : 'none',
                color: viewMode === 'flow' ? '#0f172a' : '#94a3b8',
                border: 'none',
                borderRadius: '3px',
                padding: '2px 7px',
                fontSize: '10px',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              2D Flow
            </button>
          </div>

          <button 
            onClick={handleClusterGraph} 
            disabled={isClustering || rawNodes.length === 0}
            style={{ background: '#0f766e', color: 'white', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer', opacity: isClustering ? 0.7 : 1 }}
            title="Cluster nodes by semantic topic"
          >
            {isClustering ? 'Clustering...' : 'Auto-Cluster'}
          </button>
          <button 
            onClick={handleAnalyzeGraph} 
            disabled={isAnalyzing}
            style={{ background: '#8b5cf6', color: 'white', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer', opacity: isAnalyzing ? 0.7 : 1 }}
            title="Use AI to discover concept nodes and relationships"
          >
            {isAnalyzing ? 'Analyzing...' : 'Generate Connections'}
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      {rawNodes.length > 0 && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 14px', background: '#171717', borderBottom: '1px solid #262626', gap: '8px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flex: 1 }}>
            <input
              type="text"
              placeholder="Search concepts or nodes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                maxWidth: '190px',
                padding: '3px 8px',
                fontSize: '11px',
                background: '#262626',
                border: '1px solid #404040',
                borderRadius: '4px',
                color: '#f8fafc'
              }}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                style={{ background: 'none', border: 'none', color: '#94a3b8', fontSize: '11px', cursor: 'pointer' }}
              >
                ✕
              </button>
            )}
          </div>

          <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
            <span style={{ fontSize: '10px', color: '#64748b' }}>Filter:</span>
            {['all', 'concept', 'resource', 'activity'].map((t) => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                style={{
                  background: filterType === t ? '#334155' : 'transparent',
                  color: filterType === t ? '#38bdf8' : '#94a3b8',
                  border: '1px solid',
                  borderColor: filterType === t ? '#38bdf8' : '#334155',
                  borderRadius: '3px',
                  padding: '1px 5px',
                  fontSize: '9px',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {t} {t !== 'all' && nodeStats[t] ? `(${nodeStats[t]})` : ''}
              </button>
            ))}
          </div>
        </div>
      )}
      
      {error && <p style={{ color: '#ef4444', fontSize: '12px', padding: '6px 15px', margin: 0 }}>{error}</p>}
      {successMsg && <p style={{ color: '#10b981', fontSize: '12px', padding: '6px 15px', margin: 0 }}>{successMsg}</p>}
      
      <div style={{ width: '100%', height: '380px', position: 'relative' }}>
        {rawNodes.length === 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#6b7280', fontSize: '12px', gap: '8px' }}>
            <span>No graph nodes yet.</span>
            <button
              onClick={handleAnalyzeGraph}
              disabled={isAnalyzing}
              style={{ background: '#8b5cf6', color: 'white', padding: '6px 12px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
            >
              {isAnalyzing ? 'Extracting concepts...' : 'Generate Connections with AI'}
            </button>
          </div>
        ) : viewMode === 'galaxy' ? (
          <GalaxyGraph
            nodes={rawNodes.map((n) => ({
              id: n.id,
              label: n.label,
              node_type: n.node_type || 'concept',
              description: n.description,
              confidence: n.confidence,
              is_ai_generated: n.is_ai_generated,
              x: 0,
              y: 0,
              vx: 0,
              vy: 0,
              radius: 10
            }))}
            edges={rawEdges.filter((e) => !e.is_rejected).map((e) => ({
              id: e.id,
              source: e.source_node_id,
              target: e.target_node_id,
              label: e.relationship_type,
              is_rejected: e.is_rejected
            }))}
            clusters={clusters}
            colorByCluster={colorByCluster}
            searchQuery={searchQuery}
            filterType={filterType}
            selectedNodeId={selectedNodeId}
            onSelectNode={(node: GalaxyNode | null) => setSelectedNodeId(node ? node.id : null)}
            onDeleteNode={handleDeleteNode}
            onRejectEdge={handleRejectEdge}
            onDeleteEdge={handleDeleteEdge}
          />
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
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '140px', overflowY: 'auto' }}>
            {clusters.map((c, i) => {
              const nodeCount = (c.node_ids || c.members || []).length;
              const name = c.cluster_name || c.label || `Cluster ${i + 1}`;
              return (
                <div key={i} style={{ borderLeft: `3px solid ${CLUSTER_COLORS[i % CLUSTER_COLORS.length]}`, paddingLeft: '8px' }}>
                  <strong style={{ color: '#f8fafc', fontSize: '11px' }}>{name}</strong>
                  <p style={{ margin: '2px 0 0 0', color: '#94a3b8', fontSize: '10px' }}>{c.summary}</p>
                  <div style={{ marginTop: '2px', color: '#64748b', fontSize: '9px' }}>
                    {nodeCount} nodes assigned
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphTab;
