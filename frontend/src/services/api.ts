import {
  CpuMetricsResponse,
  HealthResponse,
  LatencyMetricsResponse,
  LinkItem,
  NodeItem,
  PacketItem,
  StatisticsResponse,
  TopologyResponse,
} from '../types/api';

const API_BASE = '/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!res.ok) {
    let errorDetail = 'API Request Failed';
    try {
      const errJson = await res.json();
      errorDetail = errJson.message || errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = `HTTP ${res.status}: ${res.statusText}`;
    }
    throw new Error(errorDetail);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json();
}

export const api = {
  // Health
  getHealth: (): Promise<HealthResponse> => fetchJson<HealthResponse>('/health'),

  // Nodes
  getNodes: async (): Promise<NodeItem[]> => {
    const data = await fetchJson<{ nodes: NodeItem[]; count: number }>(`${API_BASE}/nodes`);
    return data.nodes;
  },
  createNode: (name: string): Promise<NodeItem> =>
    fetchJson<NodeItem>(`${API_BASE}/nodes`, {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),
  updateNode: (id: string, name: string): Promise<NodeItem> =>
    fetchJson<NodeItem>(`${API_BASE}/nodes/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name }),
    }),
  deleteNode: (id: string): Promise<void> =>
    fetchJson<void>(`${API_BASE}/nodes/${id}`, { method: 'DELETE' }),
  enableNode: (id: string): Promise<NodeItem> =>
    fetchJson<NodeItem>(`${API_BASE}/nodes/${id}/enable`, { method: 'POST' }),
  disableNode: (id: string): Promise<NodeItem> =>
    fetchJson<NodeItem>(`${API_BASE}/nodes/${id}/disable`, { method: 'POST' }),

  // Links
  getLinks: async (): Promise<LinkItem[]> => {
    const data = await fetchJson<{ links: LinkItem[]; count: number }>(`${API_BASE}/links`);
    return data.links;
  },
  createLink: (sourceNodeId: string, destinationNodeId: string): Promise<LinkItem> =>
    fetchJson<LinkItem>(`${API_BASE}/links`, {
      method: 'POST',
      body: JSON.stringify({
        source_node_id: sourceNodeId,
        destination_node_id: destinationNodeId,
      }),
    }),
  deleteLink: (id: string): Promise<void> =>
    fetchJson<void>(`${API_BASE}/links/${id}`, { method: 'DELETE' }),
  enableLink: (id: string): Promise<LinkItem> =>
    fetchJson<LinkItem>(`${API_BASE}/links/${id}/enable`, { method: 'POST' }),
  disableLink: (id: string): Promise<LinkItem> =>
    fetchJson<LinkItem>(`${API_BASE}/links/${id}/disable`, { method: 'POST' }),

  // Packets
  sendPacket: (sourceNodeId: string, destinationNodeId: string, payload: string): Promise<PacketItem> =>
    fetchJson<PacketItem>(`${API_BASE}/packets/send`, {
      method: 'POST',
      body: JSON.stringify({
        source_node_id: sourceNodeId,
        destination_node_id: destinationNodeId,
        payload,
      }),
    }),
  getPackets: async (): Promise<PacketItem[]> => {
    const data = await fetchJson<{ packets: PacketItem[]; count: number }>(`${API_BASE}/packets`);
    return data.packets;
  },
  getPacket: (id: string): Promise<PacketItem> =>
    fetchJson<PacketItem>(`${API_BASE}/packets/${id}`),

  // Topology
  getTopology: (): Promise<TopologyResponse> =>
    fetchJson<TopologyResponse>(`${API_BASE}/topology`),

  // Metrics
  getCpuMetrics: (): Promise<CpuMetricsResponse> =>
    fetchJson<CpuMetricsResponse>(`${API_BASE}/metrics/cpu`),
  getLatencyMetrics: (): Promise<LatencyMetricsResponse> =>
    fetchJson<LatencyMetricsResponse>(`${API_BASE}/metrics/latency`),
  getStatistics: (): Promise<StatisticsResponse> =>
    fetchJson<StatisticsResponse>(`${API_BASE}/metrics/statistics`),
};
