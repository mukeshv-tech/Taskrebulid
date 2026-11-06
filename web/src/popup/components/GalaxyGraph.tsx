import React, { useRef, useEffect, useState, useMemo } from 'react';

export interface GalaxyNode {
  id: string;
  label: string;
  node_type: 'task' | 'resource' | 'activity' | 'concept';
  clusterIndex?: number;
  // Simulation physics properties
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
}

export interface GalaxyEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
}

interface GalaxyGraphProps {
  nodes: GalaxyNode[];
  edges: GalaxyEdge[];
  clusters: any[];
  colorByCluster: boolean;
  onSelectNode?: (node: GalaxyNode) => void;
}

const CLUSTER_COLORS = [
  '#f59e0b', // amber
  '#10b981', // emerald
  '#3b82f6', // blue
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
];

const TYPE_COLORS: Record<string, { fill: string; stroke: string }> = {
  task: { fill: '#7c3aed', stroke: '#a78bfa' },
  resource: { fill: '#2563eb', stroke: '#60a5fa' },
  activity: { fill: '#059669', stroke: '#34d399' },
  concept: { fill: '#db2777', stroke: '#f472b6' }
};

export const GalaxyGraph: React.FC<GalaxyGraphProps> = ({
  nodes: initialNodes,
  edges,
  clusters,
  colorByCluster,
  onSelectNode
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Pan & Zoom Camera Transform
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [hoveredNode, setHoveredNode] = useState<GalaxyNode | null>(null);
  const [selectedNode, setSelectedNode] = useState<GalaxyNode | null>(null);

  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const draggedNodeRef = useRef<GalaxyNode | null>(null);

  // Initialize simulation nodes with positions in galaxy spiral
  const simNodes = useMemo(() => {
    return initialNodes.map((n, i) => {
      // Find cluster index
      let cIndex = -1;
      if (clusters.length > 0) {
        cIndex = clusters.findIndex((c) => {
          const ids = c.node_ids || c.members?.map((m: any) => m.node_id) || [];
          return ids.includes(n.id);
        });
      }

      // Initial spiral distribution
      const angle = i * 0.75;
      const dist = 30 + i * 18;
      const x = n.node_type === 'task' ? 0 : Math.cos(angle) * dist;
      const y = n.node_type === 'task' ? 0 : Math.sin(angle) * dist;

      return {
        ...n,
        clusterIndex: cIndex !== -1 ? cIndex : undefined,
        x,
        y,
        vx: 0,
        vy: 0,
        radius: n.node_type === 'task' ? 14 : 9
      };
    });
  }, [initialNodes, clusters]);

  // Keep live mutable reference for 60fps simulation loop
  const nodesRef = useRef<GalaxyNode[]>(simNodes);
  useEffect(() => {
    nodesRef.current = simNodes;
  }, [simNodes]);

  // Force-Directed Physics Engine Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;

    const tick = () => {
      const nodes = nodesRef.current;
      const width = canvas.width;
      const height = canvas.height;

      // 1. Repulsion force between all node pairs (Coulomb's Law)
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i];
          const b = nodes[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const distSq = dx * dx + dy * dy || 1;
          const dist = Math.sqrt(distSq);

          if (dist < 280) {
            const force = 320 / distSq;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            if (a !== draggedNodeRef.current) {
              a.vx -= fx;
              a.vy -= fy;
            }
            if (b !== draggedNodeRef.current) {
              b.vx += fx;
              b.vy += fy;
            }
          }
        }
      }

      // 2. Spring attraction force along edges (Hooke's Law)
      for (const e of edges) {
        const source = nodes.find((n) => n.id === e.source);
        const target = nodes.find((n) => n.id === e.target);
        if (source && target) {
          const dx = target.x - source.x;
          const dy = target.y - source.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const desired = 85;
          const spring = (dist - desired) * 0.035;

          const fx = (dx / dist) * spring;
          const fy = (dy / dist) * spring;

          if (source !== draggedNodeRef.current) {
            source.vx += fx;
            source.vy += fy;
          }
          if (target !== draggedNodeRef.current) {
            target.vx -= fx;
            target.vy -= fy;
          }
        }
      }

      // 3. Central gravity and dampening
      for (const node of nodes) {
        if (node === draggedNodeRef.current) continue;

        // Weak pull toward center
        node.vx -= node.x * 0.008;
        node.vy -= node.y * 0.008;

        // Friction dampening
        node.vx *= 0.88;
        node.vy *= 0.88;

        node.x += node.vx;
        node.y += node.vy;
      }

      // 4. Render Galaxy
      ctx.clearRect(0, 0, width, height);

      // Deep space cosmic gradient
      const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 20, width / 2, height / 2, width);
      bgGrad.addColorStop(0, '#0a0d14');
      bgGrad.addColorStop(1, '#020408');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      ctx.save();
      // Apply Camera Transform
      ctx.translate(width / 2 + transform.x, height / 2 + transform.y);
      ctx.scale(transform.scale, transform.scale);

      // Render Ambient Grid / Constellation Rings
      ctx.strokeStyle = 'rgba(51, 65, 85, 0.2)';
      ctx.lineWidth = 1 / transform.scale;
      ctx.beginPath();
      ctx.arc(0, 0, 75, 0, Math.PI * 2);
      ctx.arc(0, 0, 160, 0, Math.PI * 2);
      ctx.arc(0, 0, 260, 0, Math.PI * 2);
      ctx.stroke();

      // Render Edges
      for (const e of edges) {
        const source = nodes.find((n) => n.id === e.source);
        const target = nodes.find((n) => n.id === e.target);
        if (!source || !target) continue;

        const isHighlighted =
          (hoveredNode && (source.id === hoveredNode.id || target.id === hoveredNode.id)) ||
          (selectedNode && (source.id === selectedNode.id || target.id === selectedNode.id));

        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = isHighlighted ? 'rgba(56, 189, 248, 0.9)' : 'rgba(71, 85, 105, 0.45)';
        ctx.lineWidth = (isHighlighted ? 2.5 : 1) / transform.scale;
        ctx.stroke();

        // Edge label on highlight
        if (isHighlighted && e.label) {
          const midX = (source.x + target.x) / 2;
          const midY = (source.y + target.y) / 2;
          ctx.fillStyle = '#94a3b8';
          ctx.font = `${Math.max(9, 10 / transform.scale)}px sans-serif`;
          ctx.fillText(e.label, midX + 5, midY);
        }
      }

      // Render Nodes (Stars/Orbs with Cosmic Glow)
      for (const node of nodes) {
        const isHovered = hoveredNode?.id === node.id;
        const isSelected = selectedNode?.id === node.id;

        // Color determination
        let baseColor = TYPE_COLORS[node.node_type] || TYPE_COLORS.concept;
        if (colorByCluster && node.clusterIndex !== undefined) {
          const hex = CLUSTER_COLORS[node.clusterIndex % CLUSTER_COLORS.length];
          baseColor = { fill: hex, stroke: hex };
        }

        // Outer glow
        const glowRadius = (node.radius + (isHovered || isSelected ? 8 : 4));
        const glow = ctx.createRadialGradient(node.x, node.y, node.radius * 0.3, node.x, node.y, glowRadius);
        glow.addColorStop(0, baseColor.stroke);
        glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = glow;
        ctx.beginPath();
        ctx.arc(node.x, node.y, glowRadius, 0, Math.PI * 2);
        ctx.fill();

        // Node Body
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = baseColor.fill;
        ctx.fill();
        ctx.lineWidth = (isHovered || isSelected ? 2.5 : 1.5) / transform.scale;
        ctx.strokeStyle = isHovered || isSelected ? '#ffffff' : baseColor.stroke;
        ctx.stroke();

        // Text Label
        ctx.fillStyle = isHovered || isSelected ? '#ffffff' : '#cbd5e1';
        ctx.font = `${node.node_type === 'task' ? 'bold ' : ''}${Math.max(9, 11 / transform.scale)}px sans-serif`;
        ctx.textAlign = 'center';
        const displayLabel = node.label.length > 20 ? node.label.substring(0, 18) + '...' : node.label;
        ctx.fillText(displayLabel, node.x, node.y + node.radius + 12);
      }

      ctx.restore();

      animId = requestAnimationFrame(tick);
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [edges, transform, hoveredNode, selectedNode, colorByCluster]);

  // Non-passive wheel listener for smooth zooming without browser passive warnings
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.12 : 0.88;
      setTransform((prev) => ({
        ...prev,
        scale: Math.max(0.4, Math.min(3.5, prev.scale * zoomFactor))
      }));
    };

    canvas.addEventListener('wheel', onWheel, { passive: false });
    return () => {
      canvas.removeEventListener('wheel', onWheel);
    };
  }, []);

  // Coordinate Conversion helper
  const getSimCoords = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const simX = (mouseX - canvas.width / 2 - transform.x) / transform.scale;
    const simY = (mouseY - canvas.height / 2 - transform.y) / transform.scale;
    return { x: simX, y: simY };
  };

  // Mouse Handlers for Dragging & Camera Controls
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const coords = getSimCoords(e);
    const clickedNode = nodesRef.current.find((n) => {
      const dx = n.x - coords.x;
      const dy = n.y - coords.y;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius + 4;
    });

    if (clickedNode) {
      draggedNodeRef.current = clickedNode;
      setSelectedNode(clickedNode);
      if (onSelectNode) onSelectNode(clickedNode);
    } else {
      isDraggingRef.current = true;
      dragStartRef.current = { x: e.clientX - transform.x, y: e.clientY - transform.y };
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const coords = getSimCoords(e);

    if (draggedNodeRef.current) {
      draggedNodeRef.current.x = coords.x;
      draggedNodeRef.current.y = coords.y;
      draggedNodeRef.current.vx = 0;
      draggedNodeRef.current.vy = 0;
      return;
    }

    if (isDraggingRef.current) {
      setTransform((prev) => ({
        ...prev,
        x: e.clientX - dragStartRef.current.x,
        y: e.clientY - dragStartRef.current.y
      }));
      return;
    }

    // Hover detection
    const found = nodesRef.current.find((n) => {
      const dx = n.x - coords.x;
      const dy = n.y - coords.y;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius + 4;
    });
    setHoveredNode(found || null);
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
    draggedNodeRef.current = null;
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '360px', overflow: 'hidden', borderRadius: '8px' }}>
      <canvas
        ref={canvasRef}
        width={480}
        height={360}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          cursor: draggedNodeRef.current ? 'grabbing' : hoveredNode ? 'pointer' : 'grab'
        }}
      />

      {/* Floating HUD Controls */}
      <div
        style={{
          position: 'absolute',
          bottom: '10px',
          right: '10px',
          display: 'flex',
          gap: '6px',
          background: 'rgba(15, 23, 42, 0.75)',
          padding: '4px 8px',
          borderRadius: '6px',
          border: '1px solid #334155'
        }}
      >
        <button
          onClick={() => setTransform((prev) => ({ ...prev, scale: Math.min(3.5, prev.scale * 1.2) }))}
          style={{ background: 'none', border: 'none', color: '#f8fafc', cursor: 'pointer', fontSize: '13px' }}
          title="Zoom In"
        >
          +
        </button>
        <button
          onClick={() => setTransform((prev) => ({ ...prev, scale: Math.max(0.4, prev.scale * 0.8) }))}
          style={{ background: 'none', border: 'none', color: '#f8fafc', cursor: 'pointer', fontSize: '13px' }}
          title="Zoom Out"
        >
          -
        </button>
        <button
          onClick={() => setTransform({ x: 0, y: 0, scale: 1 })}
          style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '10px' }}
          title="Reset View"
        >
          Reset
        </button>
      </div>

      {/* Node Details Inspection Badge */}
      {selectedNode && (
        <div
          style={{
            position: 'absolute',
            top: '10px',
            left: '10px',
            background: 'rgba(15, 23, 42, 0.85)',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '8px 12px',
            color: '#f8fafc',
            fontSize: '11px',
            maxWidth: '220px',
            backdropFilter: 'blur(4px)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
            <span style={{ textTransform: 'uppercase', fontSize: '9px', fontWeight: 700, color: '#38bdf8' }}>
              {selectedNode.node_type}
            </span>
            <button
              onClick={() => setSelectedNode(null)}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '12px' }}
            >
              &times;
            </button>
          </div>
          <strong style={{ display: 'block', fontSize: '12px' }}>{selectedNode.label}</strong>
          {selectedNode.clusterIndex !== undefined && (
            <div style={{ marginTop: '4px', fontSize: '10px', color: CLUSTER_COLORS[selectedNode.clusterIndex % CLUSTER_COLORS.length] }}>
              ● Cluster {selectedNode.clusterIndex + 1}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
