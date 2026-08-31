import React, { useState } from 'react';
import { NodeItem, PacketItem } from '../types/api';
import { CheckCircle2, ListOrdered, XCircle } from 'lucide-react';

interface PacketLogProps {
  packets: PacketItem[];
  nodes: NodeItem[];
}

export const PacketLog: React.FC<PacketLogProps> = ({ packets, nodes }) => {
  const [filter, setFilter] = useState<'all' | 'delivered' | 'dropped'>('all');

  const nodeMap = new Map(nodes.map((n) => [n.id, n.name]));

  const filtered = packets
    .filter((p) => {
      if (filter === 'all') return true;
      return p.status === filter;
    })
    .slice(-30)
    .reverse(); // Newest first

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <ListOrdered size={16} color="#4facfe" />
          Packet Telemetry Log ({packets.length})
        </h2>

        {/* Filter Pills */}
        <div style={{ display: 'flex', gap: '4px', background: 'rgba(0,0,0,0.3)', padding: '2px', borderRadius: '6px' }}>
          <button
            type="button"
            onClick={() => setFilter('all')}
            style={{
              padding: '3px 8px',
              fontSize: '0.7rem',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer',
              background: filter === 'all' ? 'rgba(255,255,255,0.1)' : 'transparent',
              color: filter === 'all' ? '#fff' : 'var(--text-muted)',
            }}
          >
            All
          </button>
          <button
            type="button"
            onClick={() => setFilter('delivered')}
            style={{
              padding: '3px 8px',
              fontSize: '0.7rem',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer',
              background: filter === 'delivered' ? 'rgba(0,245,160,0.15)' : 'transparent',
              color: filter === 'delivered' ? '#00f5a0' : 'var(--text-muted)',
            }}
          >
            Delivered
          </button>
          <button
            type="button"
            onClick={() => setFilter('dropped')}
            style={{
              padding: '3px 8px',
              fontSize: '0.7rem',
              borderRadius: '4px',
              border: 'none',
              cursor: 'pointer',
              background: filter === 'dropped' ? 'rgba(255,75,114,0.15)' : 'transparent',
              color: filter === 'dropped' ? '#ff4b72' : 'var(--text-muted)',
            }}
          >
            Dropped
          </button>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '320px' }}>
        {filtered.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
            No packets logged yet. Send a packet above to observe dynamic routing!
          </div>
        ) : (
          filtered.map((pkt) => {
            const srcName = nodeMap.get(pkt.source_node_id) || 'Unknown';
            const dstName = nodeMap.get(pkt.destination_node_id) || 'Unknown';
            const isDelivered = pkt.status === 'delivered';

            const routeNames = pkt.path.map((id) => nodeMap.get(id) || id).join(' → ');

            return (
              <div
                key={pkt.id}
                style={{
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px',
                  padding: '10px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.75rem',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {isDelivered ? (
                    <CheckCircle2 size={16} color="#00f5a0" />
                  ) : (
                    <XCircle size={16} color="#ff4b72" />
                  )}
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                      #{pkt.sequence} [{srcName} → {dstName}]
                    </div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '2px' }}>
                      "{pkt.payload}"
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  {isDelivered ? (
                    <div>
                      <div style={{ color: '#00f5a0', fontWeight: 600 }}>{pkt.latency}ms</div>
                      <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)' }}>{routeNames}</div>
                    </div>
                  ) : (
                    <div>
                      <span className="badge badge-dropped" style={{ fontSize: '0.65rem' }}>
                        {pkt.drop_reason || 'DROPPED'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
