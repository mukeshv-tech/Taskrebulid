import codecs
import re

path = 'taskrebuild/extension/src/popup/components/GraphTab.tsx'

content = """import React, { useState, useEffect, useRef, useMemo } from 'react';
import { getTaskGraph, analyzeTaskGraph } from '../../lib/api';
import ForceGraph2D from 'react-force-graph-2d';

interface GraphTabProps {
  taskId: string;
}

const GraphTab: React.FC<GraphTabProps> = ({ taskId }) => {
  const [nodes, setNodes] = useState<any[]>([]);
  const [edges, setEdges] = useState<any[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState('');
  const [dimensions, setDimensions] = useState({ width: 400, height: 300 });
  const containerRef = useRef<HTMLDivElement>(null);
  const fgRef = useRef<any>(null);

  useEffect(() => {
    if (containerRef.current) {
      setDimensions({
        width: containerRef.current.offsetWidth,
        height: 350
      });
    }
  }, []);

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

  const validEdges = edges.filter(e => !e.is_rejected);

  const graphData = useMemo(() => {
    const gNodes = nodes.map(n => {
      let color = '#94a3b8'; // default slate
      let val = 2; // size
      if (n.node_type === 'task') { color = '#a78bfa'; val = 5; }
      else if (n.node_type === 'resource') { color = '#60a5fa'; val = 3; }
      else if (n.node_type === 'activity') { color = '#34d399'; val = 2; }
      else if (n.node_type === 'concept') { color = '#f472b6'; val = 4; }

      return {
        id: n.id,
        name: n.label,
        val,
        color,
        description: n.description
      };
    });

    const gEdges = validEdges.map(e => ({
      source: e.source_node_id,
      target: e.target_node_id,
      name: e.relationship_type
    }));

    // Filter out edges that point to missing nodes (prevents crashes)
    const validGEdges = gEdges.filter(e => 
      gNodes.find(n => n.id === e.source) && gNodes.find(n => n.id === e.target)
    );

    return { nodes: gNodes, links: validGEdges };
  }, [nodes, validEdges]);

  // Obsidian style config
  const backgroundColor = '#1e1e1e';
  const linkColor = '#555555';

  return (
    <div style={{ marginTop: '20px', background: '#1e1e1e', borderRadius: '8px', border: '1px solid #333', overflow: 'hidden' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px 15px', borderBottom: '1px solid #333', background: '#252525' }}>
        <h4 style={{ margin: 0, color: '#e5e7eb', fontSize: '13px' }}>🧠 Obsidian Map</h4>
        <button 
          onClick={handleAnalyzeGraph} 
          disabled={isAnalyzing}
          style={{ background: '#3b82f6', color: 'white', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
        >
          {isAnalyzing ? 'Analyzing...' : 'Generate Connections'}
        </button>
      </div>
      
      {error && <p style={{ color: '#ef4444', fontSize: '12px', padding: '0 15px' }}>{error}</p>}
      
      <div ref={containerRef} style={{ width: '100%', height: '350px', position: 'relative' }}>
        {nodes.length === 0 ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#6b7280', fontSize: '12px' }}>
            No graph data. Click Generate Connections.
          </div>
        ) : (
          <ForceGraph2D
            ref={fgRef}
            width={dimensions.width}
            height={dimensions.height}
            graphData={graphData}
            backgroundColor={backgroundColor}
            linkColor={() => linkColor}
            linkOpacity={0.6}
            linkWidth={1}
            nodeLabel="name"
            nodeColor="color"
            nodeRelSize={4}
            onNodeClick={(node: any) => {
              // Center node on click
              if (fgRef.current) {
                fgRef.current.centerAt(node.x, node.y, 1000);
                fgRef.current.zoom(4, 2000);
              }
            }}
            onEngineStop={() => {
              // Zoom to fit once layout settles
              if (fgRef.current) {
                fgRef.current.zoomToFit(400, 20);
              }
            }}
          />
        )}
      </div>
      <div style={{ padding: '8px 15px', background: '#252525', borderTop: '1px solid #333', display: 'flex', gap: '15px', fontSize: '10px' }}>
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
