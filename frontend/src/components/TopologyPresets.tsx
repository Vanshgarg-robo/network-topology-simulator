import React from 'react';
import { CircleDot, GitFork, Grid3X3, Layers, Network, X } from 'lucide-react';

interface TopologyPresetsProps {
  isOpen: boolean;
  onClose: () => void;
  onApplyPreset: (presetName: 'mesh' | 'ring' | 'star' | 'tree' | 'default') => Promise<void>;
  isLoading: boolean;
}

export const TopologyPresets: React.FC<TopologyPresetsProps> = ({
  isOpen,
  onClose,
  onApplyPreset,
  isLoading,
}) => {
  if (!isOpen) return null;

  const presets = [
    {
      id: 'default' as const,
      name: 'Default Topology',
      desc: 'Standard 5-node reference network (A, B, C, D, E) with redundant links.',
      icon: <Network size={20} color="#00f2fe" />,
    },
    {
      id: 'mesh' as const,
      name: 'Full Mesh Topology',
      desc: 'High resilience where every node connects directly to every other node.',
      icon: <Grid3X3 size={20} color="#00f5a0" />,
    },
    {
      id: 'ring' as const,
      name: 'Ring Topology',
      desc: 'Circular network loop where each node connects to exactly two neighbors.',
      icon: <CircleDot size={20} color="#f6d365" />,
    },
    {
      id: 'star' as const,
      name: 'Star (Hub & Spoke)',
      desc: 'Central Core Hub connected to multiple edge nodes.',
      icon: <Layers size={20} color="#9d4edd" />,
    },
    {
      id: 'tree' as const,
      name: 'Hierarchical Tree',
      desc: 'Core root switch connected to distribution and access layer nodes.',
      icon: <GitFork size={20} color="#4facfe" />,
    },
  ];

  const handleSelect = async (presetId: 'mesh' | 'ring' | 'star' | 'tree' | 'default') => {
    await onApplyPreset(presetId);
    onClose();
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
          maxWidth: '520px',
          padding: '24px',
          boxShadow: '0 20px 50px rgba(0,0,0,0.8)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Load Topology Preset</h3>
          <button
            type="button"
            onClick={onClose}
            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}
          >
            <X size={18} />
          </button>
        </div>

        <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
          Instantly reconfigure the simulation graph with classic network design patterns.
        </p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {presets.map((p) => (
            <button
              key={p.id}
              type="button"
              disabled={isLoading}
              onClick={() => handleSelect(p.id)}
              style={{
                background: 'rgba(0, 0, 0, 0.3)',
                border: '1px solid var(--border-color)',
                borderRadius: '8px',
                padding: '14px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                cursor: 'pointer',
                textAlign: 'left',
                color: 'var(--text-main)',
                transition: 'all 0.2s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'rgba(0,242,254,0.4)';
                e.currentTarget.style.background = 'rgba(0,242,254,0.05)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--border-color)';
                e.currentTarget.style.background = 'rgba(0,0,0,0.3)';
              }}
            >
              <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(255,255,255,0.05)' }}>
                {p.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{p.name}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2px' }}>{p.desc}</div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
