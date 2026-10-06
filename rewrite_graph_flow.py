import codecs
import re

path = 'taskrebuild/extension/src/popup/components/GraphTab.tsx'

content = """import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { getTaskGraph, analyzeTaskGraph } from '../../lib/api';
import { ReactFlow, Controls, Background, MarkerType, applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

interface GraphTabProps {
  taskId: string;
}

const GraphTab: React.FC<GraphTabProps> = ({ taskId }) => {
  const [rawNodes, setRawNodes] = useState<any[]>([]);
  const [rawEdges, setRawEdges] = useState<any[]>([]);
  
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');

  const loadGraph = async () => {
    try {
      setError('');
      const data = await getTaskGraph(taskId);
      setRawNodes(data.nodes || []);
      setRawEdges(data.edges || []);
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
      let color = '#334155'; // default slate
      let border = '#94a3b8';
      
      if (n.node_type === 'task') { color = '#5b21b6'; border = '#8b5cf6'; }
      else if (n.node_type === 'resource') { color = '#1e3a8a'; border = '#3b82f6'; }
      else if (n.node_type === 'activity') { color = '#064e3b'; border = '#10b981'; }
      else if (n.node_type === 'concept') { color = '#831843'; border = '#f43f5e'; }

      // Position logic: Put task in center, others in a circle
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
          background: color,
          color: '#f8fafc',
          border: `1px solid ${border}`,
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
    
    // Validate edges
    const safeEdges = flowEdges.filter(e => 
      flowNodes.find(n => n.id === e.source) && flowNodes.find(n => n.id === e.target)
    );

    setNodes(flowNodes);
    setEdges(safeEdges);
  }, [rawNodes, rawEdges]);

  const onNodesChange = useCallback((changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);

  return (
    <div style={{ marginTop: '20px', background: '#121212', borderRadius: '8px', border: '1px solid #333', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 15px', borderBottom: '1px solid #333', background: '#1e1e1e' }}>
        <h4 style={{ margin: 0, color: '#e5e7eb', fontSize: '13px' }}>🧠 Obsidian Map</h4>
        <button 
          onClick={handleAnalyzeGraph} 
          disabled={isAnalyzing}
          style={{ background: '#8b5cf6', color: 'white', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer', opacity: isAnalyzing ? 0.7 : 1 }}
        >
          {isAnalyzing ? 'Analyzing...' : 'Generate Connections'}
        </button>
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
      
      <div style={{ padding: '8px 15px', background: '#1e1e1e', borderTop: '1px solid #333', display: 'flex', gap: '15px', fontSize: '10px' }}>
        <span style={{ color: '#a78bfa' }}>● Task</span>
        <span style={{ color: '#60a5fa' }}>● Resource</span>
        <span style={{ color: '#34d399' }}>● Activity</span>
        <span style={{ color: '#f472b6' }}>● Concept</span>
      </div>
    </div>
  );
};

export default GraphTab;
"""

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

def fix_newlines(path):
    with open(path, 'rb') as f:
        file_content = f.read()
    file_content = file_content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(file_content)
fix_newlines(path)
