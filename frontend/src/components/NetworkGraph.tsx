import React, { useEffect, useRef, useState } from 'react';
import { AnimatedPacket, LinkItem, NodeItem } from '../types/api';
import { Power, Trash2, Unlink, Zap } from 'lucide-react';

interface NetworkGraphProps {
  nodes: NodeItem[];
  links: LinkItem[];
  activePackets: AnimatedPacket[];
  onToggleNode: (id: string, currentStatus: string) => void;
  onToggleLink: (id: string, currentStatus: string) => void;
  onDeleteNode: (id: string) => void;
  onDeleteLink: (id: string) => void;
  onCreateLink: (sourceId: string, destId: string) => void;
}

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  nodes,
  links,
  activePackets,
  onToggleNode,
  onToggleLink,
  onDeleteNode,
  onDeleteLink,
  onCreateLink,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Layout node positions mapped by ID
  const [positions, setPositions] = useState<{ [id: string]: { x: number; y: number } }>({});
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Connect Mode (click node 1 then node 2)
  const [connectSourceId, setConnectSourceId] = useState<string | null>(null);

  // Selected Node for detailed inspection overlay
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  // Initialize or maintain circular / radial default coordinates for nodes
  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    const width = containerRef.current.clientWidth || 800;
    const height = containerRef.current.clientHeight || 500;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.35;

    setPositions((prev) => {
      const next = { ...prev };
      nodes.forEach((node, i) => {
        if (!next[node.id]) {
          const angle = (i / nodes.length) * 2 * Math.PI - Math.PI / 2;
          next[node.id] = {
            x: centerX + radius * Math.cos(angle),
            y: centerY + radius * Math.sin(angle),
          };
        }
      });
      return next;
    });
  }, [nodes]);

  // Dragging handlers
  const handleMouseDown = (nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (connectSourceId) {
      if (connectSourceId !== nodeId) {
        onCreateLink(connectSourceId, nodeId);
      }
      setConnectSourceId(null);
      return;
    }

    const pos = positions[nodeId] || { x: 0, y: 0 };
    setDraggingNodeId(nodeId);
    setDragOffset({
      x: e.clientX - pos.x,
      y: e.clientY - pos.y,
    });
    setSelectedNodeId(nodeId);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!draggingNodeId) return;
    const newX = e.clientX - dragOffset.x;
    const newY = e.clientY - dragOffset.y;

    setPositions((prev) => ({
      ...prev,
      [draggingNodeId]: { x: newX, y: newY },
    }));
  };

  const handleMouseUp = () => {
    setDraggingNodeId(null);
  };

  // Canvas render loop for glowing links, particles, and packet traversal
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // 1. Draw Links
      links.forEach((link) => {
        const p1 = positions[link.source_node_id];
        const p2 = positions[link.destination_node_id];
        if (!p1 || !p2) return;

        const isActive = link.status === 'active';
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);

        if (isActive) {
          ctx.strokeStyle = 'rgba(0, 242, 254, 0.4)';
          ctx.lineWidth = 2.5;
          ctx.setLineDash([]);
          ctx.shadowColor = '#00f2fe';
          ctx.shadowBlur = 6;
        } else {
          ctx.strokeStyle = 'rgba(255, 75, 114, 0.5)';
          ctx.lineWidth = 2;
          ctx.setLineDash([6, 6]);
          ctx.shadowColor = '#ff4b72';
          ctx.shadowBlur = 4;
        }

        ctx.stroke();
        ctx.restore();
      });

      // 2. Draw Active Animated Packets
      activePackets.forEach((pkt) => {
        if (!pkt.path || pkt.path.length < 2) {
          const p = positions[pkt.sourceId];
          if (p) {
            ctx.save();
            ctx.beginPath();
            ctx.arc(p.x, p.y, 14, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 75, 114, 0.8)';
            ctx.shadowColor = '#ff4b72';
            ctx.shadowBlur = 12;
            ctx.fill();
            ctx.restore();
          }
          return;
        }

        const totalHops = pkt.path.length - 1;
        const currentHop = Math.min(pkt.currentHopIndex, totalHops - 1);
        const fromNodeId = pkt.path[currentHop];
        const toNodeId = pkt.path[currentHop + 1];

        const pFrom = positions[fromNodeId];
        const pTo = positions[toNodeId];

        if (pFrom && pTo) {
          const x = pFrom.x + (pTo.x - pFrom.x) * pkt.progress;
          const y = pFrom.y + (pTo.y - pFrom.y) * pkt.progress;

          ctx.save();
          ctx.beginPath();
          ctx.arc(x, y, 7, 0, Math.PI * 2);

          const isDropped = pkt.status === 'dropped';
          ctx.fillStyle = isDropped ? '#ff4b72' : '#00f5a0';
          ctx.shadowColor = isDropped ? '#ff4b72' : '#00f5a0';
          ctx.shadowBlur = 15;
          ctx.fill();

          ctx.beginPath();
          ctx.arc(x, y, 12, 0, Math.PI * 2);
          ctx.strokeStyle = isDropped ? 'rgba(255,75,114,0.4)' : 'rgba(0,245,160,0.4)';
          ctx.lineWidth = 2;
          ctx.stroke();

          ctx.restore();
        }
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [positions, links, activePackets]);

  // Keep canvas size synced with container
  useEffect(() => {
    if (!containerRef.current || !canvasRef.current) return;
    canvasRef.current.width = containerRef.current.clientWidth;
    canvasRef.current.height = containerRef.current.clientHeight;
  });

  const selectedNode = nodes.find((n) => n.id === selectedNodeId);

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      style={{
        position: 'relative',
        width: '100%',
        height: '560px',
        overflow: 'hidden',
        userSelect: 'none',
        background: 'radial-gradient(ellipse at center, rgba(17,24,39,0.85) 0%, rgba(10,14,23,0.95) 100%)',
      }}
      className="glass-panel"
      onClick={() => {
        setSelectedNodeId(null);
        setConnectSourceId(null);
      }}
    >
      {/* Top Banner Toolbar inside canvas */}
      <div style={{ position: 'absolute', top: '16px', left: '20px', zIndex: 10, display: 'flex', gap: '10px', alignItems: 'center' }}>
        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'rgba(0,0,0,0.5)', padding: '6px 12px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
          {connectSourceId ? (
            <span style={{ color: '#f6d365' }}>⚡ Click target node to establish link...</span>
          ) : (
            <span>💡 Drag nodes to rearrange • Click link/node to toggle failure</span>
          )}
        </div>
      </div>

      {/* HTML5 Canvas overlay for link lines & packet particles */}
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
        }}
      />

      {/* Interactive SVG / HTML Nodes */}
      {nodes.map((node) => {
        const pos = positions[node.id] || { x: 100, y: 100 };
        const isOnline = node.status === 'online';
        const isSelected = selectedNodeId === node.id;
        const isConnectSource = connectSourceId === node.id;

        return (
          <div
            key={node.id}
            onMouseDown={(e) => handleMouseDown(node.id, e)}
            style={{
              position: 'absolute',
              left: `${pos.x - 30}px`,
              top: `${pos.y - 30}px`,
              width: '60px',
              height: '60px',
              borderRadius: '50%',
              background: isOnline
                ? 'radial-gradient(circle, #1e293b 40%, #0f172a 100%)'
                : 'radial-gradient(circle, #3b1e24 40%, #1a0f12 100%)',
              border: isConnectSource
                ? '3px solid #f6d365'
                : isSelected
                ? '3px solid #00f2fe'
                : isOnline
                ? '2px solid rgba(0, 245, 160, 0.6)'
                : '2px solid rgba(255, 75, 114, 0.6)',
              boxShadow: isOnline
                ? isSelected
                  ? '0 0 25px rgba(0, 242, 254, 0.8)'
                  : '0 0 15px rgba(0, 245, 160, 0.3)'
                : '0 0 15px rgba(255, 75, 114, 0.4)',
              cursor: connectSourceId ? 'crosshair' : 'grab',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: isSelected ? 20 : 5,
              transition: draggingNodeId === node.id ? 'none' : 'border-color 0.2s, box-shadow 0.2s',
            }}
          >
            <div style={{ fontSize: '0.85rem', fontWeight: 700, color: isOnline ? '#fff' : '#f87171' }}>
              {node.name}
            </div>
            <div style={{ fontSize: '0.65rem', color: isOnline ? '#00f5a0' : '#ff4b72', fontWeight: 600 }}>
              {isOnline ? `${Math.round(node.cpu_usage)}%` : 'OFF'}
            </div>
          </div>
        );
      })}

      {/* Link Midpoint Click Targets for Status Toggle / Deletion */}
      {links.map((link) => {
        const p1 = positions[link.source_node_id];
        const p2 = positions[link.destination_node_id];
        if (!p1 || !p2) return null;

        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        const isActive = link.status === 'active';

        return (
          <div
            key={link.id}
            onClick={(e) => {
              e.stopPropagation();
              onToggleLink(link.id, link.status);
            }}
            onContextMenu={(e) => {
              e.preventDefault();
              e.stopPropagation();
              if (confirm('Delete this network link?')) {
                onDeleteLink(link.id);
              }
            }}
            title={`Link status: ${link.status} (Left-click toggle, Right-click delete)`}
            style={{
              position: 'absolute',
              left: `${midX - 12}px`,
              top: `${midY - 12}px`,
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              background: isActive ? 'rgba(17, 24, 39, 0.9)' : 'rgba(255, 75, 114, 0.2)',
              border: isActive ? '1px solid rgba(0,242,254,0.5)' : '1px solid #ff4b72',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              zIndex: 8,
              boxShadow: '0 2px 8px rgba(0,0,0,0.5)',
            }}
          >
            {isActive ? <Zap size={11} color="#00f2fe" /> : <Unlink size={11} color="#ff4b72" />}
          </div>
        );
      })}

      {/* Node Context Card Overlay */}
      {selectedNode && (
        <div
          onClick={(e) => e.stopPropagation()}
          className="glass-panel"
          style={{
            position: 'absolute',
            bottom: '20px',
            left: '20px',
            padding: '16px 20px',
            minWidth: '260px',
            zIndex: 30,
            boxShadow: '0 10px 30px rgba(0,0,0,0.7)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Node: {selectedNode.name}</h3>
            <span className={`badge ${selectedNode.status === 'online' ? 'badge-online' : 'badge-offline'}`}>
              {selectedNode.status}
            </span>
          </div>

          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '12px' }}>
            <div>CPU Load: <strong style={{ color: '#00f5a0' }}>{selectedNode.cpu_usage.toFixed(1)}%</strong></div>
            <div style={{ fontSize: '0.7rem', wordBreak: 'break-all', marginTop: '4px', opacity: 0.7 }}>
              ID: {selectedNode.id}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            <button
              className={`btn ${selectedNode.status === 'online' ? 'btn-danger' : 'btn-success'}`}
              style={{ fontSize: '0.75rem', padding: '6px 10px' }}
              onClick={() => onToggleNode(selectedNode.id, selectedNode.status)}
            >
              <Power size={13} />
              {selectedNode.status === 'online' ? 'Disable' : 'Enable'}
            </button>

            <button
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '6px 10px' }}
              onClick={() => setConnectSourceId(selectedNode.id)}
            >
              <Zap size={13} color="#f6d365" />
              Link to...
            </button>

            <button
              className="btn btn-secondary"
              style={{ fontSize: '0.75rem', padding: '6px 10px', color: '#ff4b72' }}
              onClick={() => {
                onDeleteNode(selectedNode.id);
                setSelectedNodeId(null);
              }}
            >
              <Trash2 size={13} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
