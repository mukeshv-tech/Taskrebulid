import React, { useRef, useEffect, useState, useMemo } from 'react';

export interface GalaxyNode {
  id: string;
  label: string;
  node_type: 'task' | 'resource' | 'activity' | 'concept';
  clusterIndex?: number;
  description?: string;
  confidence?: number;
  is_ai_generated?: boolean;
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
  is_rejected?: boolean;
}

interface GalaxyGraphProps {
  nodes: GalaxyNode[];
  edges: GalaxyEdge[];
  clusters: any[];
  colorByCluster: boolean;
  searchQuery?: string;
  filterType?: string;
  selectedNodeId?: string | null;
  onSelectNode?: (node: GalaxyNode | null) => void;
  onDeleteNode?: (nodeId: string) => void;
  onRejectEdge?: (edgeId: string) => void;
  onDeleteEdge?: (edgeId: string) => void;
}

const CLUSTER_COLORS = [
  '#f59e0b', // amber
  '#10b981', // emerald
  '#3b82f6', // blue
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#06b6d4', // cyan
];

const TYPE_COLORS: Record<string, { fill: string; stroke: string; label: string }> = {
  task: { fill: '#7c3aed', stroke: '#a78bfa', label: 'Task' },
  resource: { fill: '#2563eb', stroke: '#60a5fa', label: 'Resource' },
  activity: { fill: '#059669', stroke: '#34d399', label: 'Activity' },
  concept: { fill: '#db2777', stroke: '#f472b6', label: 'Concept' }
};

export const GalaxyGraph: React.FC<GalaxyGraphProps> = ({
  nodes: initialNodes,
  edges,
  clusters,
  colorByCluster,
  searchQuery = '',
  filterType = 'all',
  selectedNodeId,
  onSelectNode,
  onDeleteNode,
  onRejectEdge,
  onDeleteEdge
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  // Pan & Zoom Camera Transform
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const [hoveredNode, setHoveredNode] = useState<GalaxyNode | null>(null);
  const [internalSelectedNode, setInternalSelectedNode] = useState<GalaxyNode | null>(null);

  const isDraggingRef = useRef(false);
  const dragStartRef = useRef({ x: 0, y: 0 });
  const draggedNodeRef = useRef<GalaxyNode | null>(null);
  const alphaRef = useRef(1.0); // Simulation energy for smooth cooling

  // Sync external selectedNodeId if supplied
  useEffect(() => {
    if (selectedNodeId) {
      const match = initialNodes.find((n) => n.id === selectedNodeId);
      if (match) setInternalSelectedNode(match);
    } else if (selectedNodeId === null) {
      setInternalSelectedNode(null);
    }
  }, [selectedNodeId, initialNodes]);

  const activeSelected = internalSelectedNode;

  // Initialize simulation nodes with positions in galaxy spiral
  const simNodes = useMemo(() => {
    return initialNodes.map((n, i) => {
      let cIndex = -1;
      if (clusters.length > 0) {
        cIndex = clusters.findIndex((c) => {
          const ids = c.node_ids || c.members?.map((m: any) => m.node_id) || [];
          return ids.includes(n.id);
        });
      }

      const angle = i * 0.75;
      const dist = 35 + i * 18;
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
    alphaRef.current = 1.0; // Re-energize simulation when nodes change
  }, [simNodes]);

  // Re-energize when user drags or searches
  const reEnergize = () => {
    if (alphaRef.current < 0.2) {
      alphaRef.current = 0.45;
    }
  };

  // Force-Directed Physics Engine Loop with Energy Decay (Cooling)
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
      const currentAlpha = alphaRef.current;

      // Only calculate physics while simulation has energy (prevents permanent jitter)
      if (currentAlpha > 0.003 || draggedNodeRef.current) {
        // 1. Repulsion force between all node pairs
        for (let i = 0; i < nodes.length; i++) {
          for (let j = i + 1; j < nodes.length; j++) {
            const a = nodes[i];
            const b = nodes[j];
            const dx = b.x - a.x;
            const dy = b.y - a.y;
            const distSq = dx * dx + dy * dy || 1;
            const dist = Math.sqrt(distSq);

            if (dist < 260) {
              const force = (300 / distSq) * currentAlpha;
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

        // 2. Spring attraction force along edges
        for (const e of edges) {
          const source = nodes.find((n) => n.id === e.source);
          const target = nodes.find((n) => n.id === e.target);
          if (source && target) {
            const dx = target.x - source.x;
            const dy = target.y - source.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const desired = 80;
            const spring = (dist - desired) * 0.03 * currentAlpha;

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

          // Pull toward center
          node.vx -= node.x * 0.007 * currentAlpha;
          node.vy -= node.y * 0.007 * currentAlpha;

          // Velocity dampening
          node.vx *= 0.86;
          node.vy *= 0.86;

          node.x += node.vx;
          node.y += node.vy;
        }

        // Decay simulation energy gradually
        if (!draggedNodeRef.current) {
          alphaRef.current *= 0.985;
        }
      }

      // 4. Render Canvas Frame
      ctx.clearRect(0, 0, width, height);

      // Deep space cosmic gradient
      const bgGrad = ctx.createRadialGradient(width / 2, height / 2, 20, width / 2, height / 2, width);
      bgGrad.addColorStop(0, '#0a0d14');
      bgGrad.addColorStop(1, '#020408');
      ctx.fillStyle = bgGrad;
      ctx.fillRect(0, 0, width, height);

      ctx.save();
      ctx.translate(width / 2 + transform.x, height / 2 + transform.y);
      ctx.scale(transform.scale, transform.scale);

      // Constellation Guide Rings
      ctx.strokeStyle = 'rgba(51, 65, 85, 0.2)';
      ctx.lineWidth = 1 / transform.scale;
      ctx.beginPath();
      ctx.arc(0, 0, 75, 0, Math.PI * 2);
      ctx.arc(0, 0, 160, 0, Math.PI * 2);
      ctx.arc(0, 0, 260, 0, Math.PI * 2);
      ctx.stroke();

      const normalizedSearch = searchQuery.trim().toLowerCase();

      // Helper to check visibility based on search & filter
      const isNodeVisible = (node: GalaxyNode) => {
        if (filterType !== 'all' && node.node_type !== filterType) return false;
        if (normalizedSearch && !node.label.toLowerCase().includes(normalizedSearch)) return false;
        return true;
      };

      // Render Edges
      for (const e of edges) {
        const source = nodes.find((n) => n.id === e.source);
        const target = nodes.find((n) => n.id === e.target);
        if (!source || !target) continue;

        const sourceVisible = isNodeVisible(source);
        const targetVisible = isNodeVisible(target);

        const isHighlighted =
          (hoveredNode && (source.id === hoveredNode.id || target.id === hoveredNode.id)) ||
          (activeSelected && (source.id === activeSelected.id || target.id === activeSelected.id));

        const baseAlpha = (!sourceVisible || !targetVisible) ? 0.08 : (isHighlighted ? 0.9 : 0.4);

        ctx.beginPath();
        ctx.moveTo(source.x, source.y);
        ctx.lineTo(target.x, target.y);
        ctx.strokeStyle = isHighlighted ? 'rgba(56, 189, 248, 0.95)' : `rgba(71, 85, 105, ${baseAlpha})`;
        ctx.lineWidth = (isHighlighted ? 2.5 : 1) / transform.scale;
        ctx.stroke();

        // Edge label on hover or select
        if (isHighlighted && e.label) {
          const midX = (source.x + target.x) / 2;
          const midY = (source.y + target.y) / 2;
          ctx.fillStyle = '#38bdf8';
          ctx.font = `600 ${Math.max(9, 10 / transform.scale)}px sans-serif`;
          ctx.fillText(e.label, midX + 6, midY);
        }
      }

      // Render Nodes
      for (const node of nodes) {
        const isHovered = hoveredNode?.id === node.id;
        const isSelected = activeSelected?.id === node.id;
        const isMatch = isNodeVisible(node);

        let baseColor = TYPE_COLORS[node.node_type] || TYPE_COLORS.concept;
        if (colorByCluster && node.clusterIndex !== undefined) {
          const hex = CLUSTER_COLORS[node.clusterIndex % CLUSTER_COLORS.length];
          baseColor = { fill: hex, stroke: hex, label: `Cluster ${node.clusterIndex + 1}` };
        }

        ctx.globalAlpha = isMatch ? 1 : 0.15;

        // Outer glow
        const glowRadius = node.radius + (isHovered || isSelected ? 9 : 4);
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

        // Label text
        ctx.fillStyle = isHovered || isSelected ? '#ffffff' : (isMatch ? '#cbd5e1' : '#64748b');
        ctx.font = `${node.node_type === 'task' ? 'bold ' : ''}${Math.max(9, 11 / transform.scale)}px sans-serif`;
        ctx.textAlign = 'center';
        const displayLabel = node.label.length > 20 ? node.label.substring(0, 18) + '...' : node.label;
        ctx.fillText(displayLabel, node.x, node.y + node.radius + 12);
        ctx.globalAlpha = 1.0;
      }

      ctx.restore();
      animId = requestAnimationFrame(tick);
    };

    animId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(animId);
  }, [edges, transform, hoveredNode, activeSelected, colorByCluster, searchQuery, filterType]);

  // Zoom with wheel
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.12 : 0.88;
      setTransform((prev) => ({
        ...prev,
        scale: Math.max(0.35, Math.min(3.5, prev.scale * zoomFactor))
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

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const coords = getSimCoords(e);
    const clickedNode = nodesRef.current.find((n) => {
      const dx = n.x - coords.x;
      const dy = n.y - coords.y;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius + 5;
    });

    if (clickedNode) {
      draggedNodeRef.current = clickedNode;
      setInternalSelectedNode(clickedNode);
      if (onSelectNode) onSelectNode(clickedNode);
      reEnergize();
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
      reEnergize();
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

    const found = nodesRef.current.find((n) => {
      const dx = n.x - coords.x;
      const dy = n.y - coords.y;
      return Math.sqrt(dx * dx + dy * dy) <= n.radius + 5;
    });
    setHoveredNode(found || null);
  };

  const handleMouseUp = () => {
    isDraggingRef.current = false;
    draggedNodeRef.current = null;
  };

  // Connected edges for selected node
  const connectedEdges = useMemo(() => {
    if (!activeSelected) return [];
    return edges.filter((e) => e.source === activeSelected.id || e.target === activeSelected.id);
  }, [activeSelected, edges]);

  return (
    <div style={{ position: 'relative', width: '100%', height: '380px', overflow: 'hidden', borderRadius: '8px' }}>
      <canvas
        ref={canvasRef}
        width={500}
        height={380}
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
          gap: '4px',
          background: 'rgba(15, 23, 42, 0.85)',
          padding: '3px 6px',
          borderRadius: '6px',
          border: '1px solid #334155',
          zIndex: 5
        }}
      >
        <button
          onClick={() => setTransform((prev) => ({ ...prev, scale: Math.min(3.5, prev.scale * 1.2) }))}
          style={{ background: 'none', border: 'none', color: '#f8fafc', cursor: 'pointer', fontSize: '13px', padding: '2px 5px' }}
          title="Zoom In"
        >
          +
        </button>
        <button
          onClick={() => setTransform((prev) => ({ ...prev, scale: Math.max(0.35, prev.scale * 0.8) }))}
          style={{ background: 'none', border: 'none', color: '#f8fafc', cursor: 'pointer', fontSize: '13px', padding: '2px 5px' }}
          title="Zoom Out"
        >
          -
        </button>
        <button
          onClick={() => {
            setTransform({ x: 0, y: 0, scale: 1 });
            reEnergize();
          }}
          style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '10px', padding: '2px 5px' }}
          title="Reset View"
        >
          Reset
        </button>
      </div>

      {/* Node Inspector Side Panel */}
      {activeSelected && (
        <div
          style={{
            position: 'absolute',
            top: '10px',
            left: '10px',
            width: '230px',
            maxHeight: '340px',
            background: 'rgba(15, 23, 42, 0.94)',
            border: '1px solid #334155',
            borderRadius: '6px',
            padding: '10px',
            color: '#f8fafc',
            fontSize: '11px',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
            backdropFilter: 'blur(8px)',
            overflowY: 'auto',
            zIndex: 10
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span
              style={{
                textTransform: 'uppercase',
                fontSize: '9px',
                fontWeight: 700,
                color: (TYPE_COLORS[activeSelected.node_type] || TYPE_COLORS.concept).stroke,
                letterSpacing: '0.5px'
              }}
            >
              {activeSelected.node_type}
            </span>
            <button
              onClick={() => {
                setInternalSelectedNode(null);
                if (onSelectNode) onSelectNode(null);
              }}
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '14px', lineHeight: 1 }}
              title="Close panel"
            >
              &times;
            </button>
          </div>

          <strong style={{ display: 'block', fontSize: '13px', wordBreak: 'break-word', color: '#ffffff', marginBottom: '4px' }}>
            {activeSelected.label}
          </strong>

          {activeSelected.description && (
            <p style={{ margin: '0 0 8px 0', fontSize: '10px', color: '#94a3b8', lineHeight: 1.4 }}>
              {activeSelected.description}
            </p>
          )}

          {activeSelected.clusterIndex !== undefined && (
            <div
              style={{
                marginBottom: '8px',
                fontSize: '10px',
                display: 'inline-block',
                padding: '2px 6px',
                borderRadius: '4px',
                background: 'rgba(30, 41, 59, 0.8)',
                color: CLUSTER_COLORS[activeSelected.clusterIndex % CLUSTER_COLORS.length],
                fontWeight: 600
              }}
            >
              ● Cluster {activeSelected.clusterIndex + 1}
            </div>
          )}

          {/* Connected Relationships */}
          <div style={{ marginTop: '8px', borderTop: '1px solid #334155', paddingTop: '6px' }}>
            <span style={{ fontSize: '10px', color: '#64748b', fontWeight: 600 }}>CONNECTIONS ({connectedEdges.length})</span>
            {connectedEdges.length === 0 ? (
              <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '10px' }}>No direct connections</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '4px' }}>
                {connectedEdges.map((e) => {
                  const isSource = e.source === activeSelected.id;
                  const otherId = isSource ? e.target : e.source;
                  const otherNode = nodesRef.current.find((n) => n.id === otherId);
                  const otherLabel = otherNode ? otherNode.label : otherId;

                  return (
                    <div
                      key={e.id}
                      style={{
                        padding: '4px 6px',
                        background: '#1e293b',
                        borderRadius: '4px',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        gap: '4px'
                      }}
                    >
                      <div style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '140px' }}>
                        <span style={{ color: '#38bdf8', fontSize: '9px', display: 'block' }}>
                          {isSource ? '→ ' : '← '} {e.label || 'connected to'}
                        </span>
                        <span style={{ color: '#e2e8f0', fontSize: '10px' }}>{otherLabel}</span>
                      </div>
                      <div style={{ display: 'flex', gap: '2px' }}>
                        {onRejectEdge && (
                          <button
                            onClick={() => onRejectEdge(e.id)}
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: '#f59e0b',
                              fontSize: '10px',
                              cursor: 'pointer',
                              padding: '1px 3px'
                            }}
                            title="Reject connection"
                          >
                            ⊘
                          </button>
                        )}
                        {onDeleteEdge && (
                          <button
                            onClick={() => onDeleteEdge(e.id)}
                            style={{
                              background: 'transparent',
                              border: 'none',
                              color: '#ef4444',
                              fontSize: '11px',
                              cursor: 'pointer',
                              padding: '1px 3px'
                            }}
                            title="Delete connection"
                          >
                            ×
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Node Actions */}
          {onDeleteNode && activeSelected.node_type !== 'task' && (
            <div style={{ marginTop: '10px', borderTop: '1px solid #334155', paddingTop: '6px' }}>
              <button
                onClick={() => onDeleteNode(activeSelected.id)}
                style={{
                  width: '100%',
                  padding: '4px',
                  background: 'rgba(239, 68, 68, 0.15)',
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                  borderRadius: '4px',
                  color: '#f87171',
                  fontSize: '10px',
                  cursor: 'pointer',
                  fontWeight: 600
                }}
              >
                Delete Node
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
