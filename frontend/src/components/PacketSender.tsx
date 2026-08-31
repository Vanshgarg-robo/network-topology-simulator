import React, { useState } from 'react';
import { NodeItem } from '../types/api';
import { Flame, Play, Send, Shuffle } from 'lucide-react';

interface PacketSenderProps {
  nodes: NodeItem[];
  onSendPacket: (sourceId: string, destId: string, payload: string) => Promise<void>;
  onTriggerChaos: () => void;
  isLoading: boolean;
}

export const PacketSender: React.FC<PacketSenderProps> = ({
  nodes,
  onSendPacket,
  onTriggerChaos,
  isLoading,
}) => {
  const [sourceId, setSourceId] = useState<string>('');
  const [destId, setDestId] = useState<string>('');
  const [payload, setPayload] = useState<string>('Diagnostic Ping #1');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceId || !destId || !payload.trim()) return;
    await onSendPacket(sourceId, destId, payload);
  };

  const handleRandomize = () => {
    if (nodes.length < 2) return;
    const shuffled = [...nodes].sort(() => 0.5 - Math.random());
    setSourceId(shuffled[0].id);
    setDestId(shuffled[1].id);
  };

  const templates = [
    'Ping Request',
    'Telemetry Sync',
    'High Priority Payload',
    'Heartbeat Check',
  ];

  return (
    <div className="glass-panel" style={{ padding: '20px', height: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <h2 style={{ fontSize: '1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Send size={16} color="#00f2fe" />
          Packet Transmission Console
        </h2>

        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            type="button"
            className="btn btn-secondary"
            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
            onClick={handleRandomize}
            title="Pick random source and destination"
          >
            <Shuffle size={12} />
            Random
          </button>
          <button
            type="button"
            className="btn btn-danger"
            style={{ padding: '4px 8px', fontSize: '0.75rem' }}
            onClick={onTriggerChaos}
            title="Randomly toggle a node/link failure"
          >
            <Flame size={12} />
            Chaos Mode
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
              Source Node
            </label>
            <select
              className="input-field"
              value={sourceId}
              onChange={(e) => setSourceId(e.target.value)}
              required
            >
              <option value="">Select source...</option>
              {nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name} ({n.status})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
              Destination Node
            </label>
            <select
              className="input-field"
              value={destId}
              onChange={(e) => setDestId(e.target.value)}
              required
            >
              <option value="">Select destination...</option>
              {nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name} ({n.status})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
            Packet Payload
          </label>
          <input
            type="text"
            className="input-field"
            value={payload}
            onChange={(e) => setPayload(e.target.value)}
            placeholder="Enter message or telemetry payload..."
            required
          />
        </div>

        {/* Quick Templates */}
        <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
          {templates.map((tpl) => (
            <button
              key={tpl}
              type="button"
              onClick={() => setPayload(tpl)}
              style={{
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid var(--border-color)',
                borderRadius: '4px',
                padding: '3px 8px',
                fontSize: '0.7rem',
                color: 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              {tpl}
            </button>
          ))}
        </div>

        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading || !sourceId || !destId || sourceId === destId}
          style={{ width: '100%', marginTop: '4px' }}
        >
          <Play size={15} />
          {isLoading ? 'Transmitting...' : 'Dispatch Packet'}
        </button>
      </form>
    </div>
  );
};
