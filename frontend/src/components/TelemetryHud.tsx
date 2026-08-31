import React from 'react';
import { CpuMetricsResponse, LatencyMetricsResponse, StatisticsResponse } from '../types/api';
import { Clock, Cpu, Gauge } from 'lucide-react';

interface TelemetryHudProps {
  cpuMetrics: CpuMetricsResponse | null;
  latencyMetrics: LatencyMetricsResponse | null;
  stats: StatisticsResponse | null;
}

export const TelemetryHud: React.FC<TelemetryHudProps> = ({
  cpuMetrics,
  latencyMetrics,
  stats,
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {/* 1. Global Performance Stats */}
      <div className="glass-panel" style={{ padding: '18px' }}>
        <h2 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Gauge size={16} color="#00f5a0" />
          Network Telemetry & Throughput
        </h2>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px' }}>
          <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Packets Sent</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#fff' }}>{stats?.total_sent ?? 0}</div>
          </div>

          <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Delivered</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#00f5a0' }}>{stats?.total_received ?? 0}</div>
          </div>

          <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Dropped</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ff4b72' }}>{stats?.total_dropped ?? 0}</div>
          </div>

          <div style={{ padding: '10px', background: 'rgba(0,0,0,0.3)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Avg Latency</div>
            <div style={{ fontSize: '1.25rem', fontWeight: 700, color: '#00f2fe' }}>
              {latencyMetrics?.average_latency ? `${latencyMetrics.average_latency}ms` : '0ms'}
            </div>
          </div>
        </div>
      </div>

      {/* 2. Node CPU Workload Meters */}
      <div className="glass-panel" style={{ padding: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
          <h2 style={{ fontSize: '0.9rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={16} color="#9d4edd" />
            Node CPU Workload
          </h2>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Avg: <strong>{cpuMetrics?.average_cpu.toFixed(1) ?? 0}%</strong>
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '180px', overflowY: 'auto' }}>
          {cpuMetrics?.metrics && cpuMetrics.metrics.length > 0 ? (
            cpuMetrics.metrics.map((m) => {
              const usage = m.cpu_usage;
              const color = usage > 70 ? '#ff4b72' : usage > 40 ? '#f6d365' : '#00f5a0';

              return (
                <div key={m.node_id}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
                    <span>{m.node_name}</span>
                    <span style={{ fontWeight: 600, color }}>{usage.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: '6px', width: '100%', background: 'rgba(255,255,255,0.06)', borderRadius: '3px', overflow: 'hidden' }}>
                    <div
                      style={{
                        height: '100%',
                        width: `${Math.min(usage, 100)}%`,
                        background: color,
                        borderRadius: '3px',
                        transition: 'width 0.4s ease, background-color 0.4s ease',
                      }}
                    />
                  </div>
                </div>
              );
            })
          ) : (
            <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textAlign: 'center', padding: '12px' }}>
              No nodes detected.
            </div>
          )}
        </div>
      </div>

      {/* 3. Latency Distribution */}
      {latencyMetrics && latencyMetrics.metrics.length > 0 && (
        <div className="glass-panel" style={{ padding: '18px' }}>
          <h2 style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Clock size={16} color="#00f2fe" />
            Latency Bounds
          </h2>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <div>Min: <strong style={{ color: '#00f5a0' }}>{latencyMetrics.min_latency}ms</strong></div>
            <div>Avg: <strong style={{ color: '#00f2fe' }}>{latencyMetrics.average_latency}ms</strong></div>
            <div>Max: <strong style={{ color: '#ff4b72' }}>{latencyMetrics.max_latency}ms</strong></div>
          </div>
        </div>
      )}
    </div>
  );
};
