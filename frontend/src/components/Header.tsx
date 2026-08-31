import React from 'react';
import { Activity, Network, RefreshCw, Send, Sparkles } from 'lucide-react';
import { StatisticsResponse } from '../types/api';

interface HeaderProps {
  stats: StatisticsResponse | null;
  serverOnline: boolean;
  onRefresh: () => void;
  onOpenAddNode: () => void;
  onOpenAddLink: () => void;
  onOpenPresets: () => void;
  isAutoTraffic: boolean;
  onToggleAutoTraffic: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  stats,
  serverOnline,
  onRefresh,
  onOpenAddNode,
  onOpenAddLink,
  onOpenPresets,
  isAutoTraffic,
  onToggleAutoTraffic,
}) => {
  return (
    <header className="glass-panel" style={{ padding: '16px 24px', margin: '16px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
      {/* Brand & Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{
          width: '42px',
          height: '42px',
          borderRadius: '12px',
          background: 'linear-gradient(135deg, rgba(0,242,254,0.2) 0%, rgba(157,78,221,0.2) 100%)',
          border: '1px solid rgba(0,242,254,0.4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(0,242,254,0.25)',
        }}>
          <Network size={24} color="#00f2fe" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 700, letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #fff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Network Simulator
            </h1>
            <span className={`badge ${serverOnline ? 'badge-online' : 'badge-offline'}`}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: serverOnline ? '#00f5a0' : '#ff4b72', display: 'inline-block' }}></span>
              {serverOnline ? 'FastAPI Connected' : 'Disconnected'}
            </span>
          </div>
          <p style={{ fontSize: '0.775rem', color: 'var(--text-muted)' }}>
            Real-Time Dynamic Routing, Latency & CPU Simulation Platform
          </p>
        </div>
      </div>

      {/* Quick Summary Pill Strip */}
      {stats && (
        <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ padding: '6px 14px', borderRadius: '8px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
            <Network size={14} color="#00f2fe" />
            <span style={{ color: 'var(--text-muted)' }}>Topology:</span>
            <strong>{stats.total_nodes} Nodes / {stats.total_links} Links</strong>
          </div>
          <div style={{ padding: '6px 14px', borderRadius: '8px', background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem' }}>
            <Activity size={14} color="#00f5a0" />
            <span style={{ color: 'var(--text-muted)' }}>Success Rate:</span>
            <strong style={{ color: stats.delivery_rate_percent > 80 ? '#00f5a0' : '#f6d365' }}>
              {stats.delivery_rate_percent.toFixed(1)}%
            </strong>
          </div>
        </div>
      )}

      {/* Action Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
        <button
          className={`btn ${isAutoTraffic ? 'btn-danger' : 'btn-secondary'}`}
          onClick={onToggleAutoTraffic}
          title="Toggle automatic background packet burst simulation"
        >
          <Send size={15} />
          {isAutoTraffic ? 'Stop Auto-Traffic' : 'Auto-Traffic'}
        </button>

        <button className="btn btn-secondary" onClick={onOpenPresets} title="Load preset topologies (Ring, Mesh, Star)">
          <Sparkles size={15} color="#f6d365" />
          Presets
        </button>

        <button className="btn btn-secondary" onClick={onOpenAddNode}>
          + Node
        </button>

        <button className="btn btn-secondary" onClick={onOpenAddLink}>
          + Link
        </button>

        <button className="btn btn-primary" onClick={onRefresh} title="Fetch fresh telemetry">
          <RefreshCw size={15} />
          Sync
        </button>
      </div>
    </header>
  );
};
