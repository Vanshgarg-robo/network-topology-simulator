import React, { useState } from 'react';
import { NodeItem } from '../types/api';
import { X } from 'lucide-react';

interface LinkModalProps {
  isOpen: boolean;
  nodes: NodeItem[];
  onClose: () => void;
  onSubmit: (sourceId: string, destId: string) => Promise<void>;
}

export const LinkModal: React.FC<LinkModalProps> = ({ isOpen, nodes, onClose, onSubmit }) => {
  const [sourceId, setSourceId] = useState('');
  const [destId, setDestId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sourceId || !destId || sourceId === destId) return;

    try {
      setLoading(true);
      setError('');
      await onSubmit(sourceId, destId);
      setSourceId('');
      setDestId('');
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to establish link');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        backdropFilter: 'blur(6px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 100,
      }}
      onClick={onClose}
    >
      <div
        className="glass-panel"
        style={{
          width: '100%',
          maxWidth: '420px',
          padding: '24px',
          boxShadow: '0 20px 50px rgba(0,0,0,0.8)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Connect Network Link</h3>
          <button
            type="button"
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        {error && (
          <div style={{ padding: '8px 12px', background: 'rgba(255,75,114,0.15)', border: '1px solid rgba(255,75,114,0.3)', borderRadius: '6px', color: '#ff4b72', fontSize: '0.8rem', marginBottom: '14px' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
              First Node
            </label>
            <select
              className="input-field"
              value={sourceId}
              onChange={(e) => setSourceId(e.target.value)}
              required
            >
              <option value="">Select node...</option>
              {nodes.map((n) => (
                <option key={n.id} value={n.id}>
                  {n.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>
              Second Node
            </label>
            <select
              className="input-field"
              value={destId}
              onChange={(e) => setDestId(e.target.value)}
              required
            >
              <option value="">Select node...</option>
              {nodes.map((n) => (
                <option key={n.id} value={n.id} disabled={n.id === sourceId}>
                  {n.name} {n.id === sourceId ? '(Cannot link to self)' : ''}
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '10px' }}>
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !sourceId || !destId || sourceId === destId}
            >
              {loading ? 'Linking...' : 'Establish Link'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
