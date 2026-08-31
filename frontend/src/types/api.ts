export type NodeStatus = 'online' | 'offline';
export type LinkStatus = 'active' | 'down';
export type PacketStatus = 'created' | 'in_transit' | 'delivered' | 'dropped';
export type DropReason = 'SOURCE_OFFLINE' | 'DESTINATION_OFFLINE' | 'NO_ROUTE';

export interface NodeItem {
  id: string;
  name: string;
  status: NodeStatus;
  cpu_usage: number;
  created_at: string;
  x?: number;
  y?: number;
}

export interface LinkItem {
  id: string;
  source_node_id: string;
  destination_node_id: string;
  status: LinkStatus;
  created_at: string;
}

export interface PacketItem {
  id: string;
  sequence: number;
  source_node_id: string;
  destination_node_id: string;
  payload: string;
  status: PacketStatus;
  drop_reason: DropReason | null;
  path: string[];
  latency: number;
  created_at: string;
}

export interface TopologyNode {
  id: string;
  name: string;
  status: NodeStatus;
}

export interface TopologyEdge {
  id: string;
  source_node_id: string;
  destination_node_id: string;
  status: LinkStatus;
}

export interface TopologyResponse {
  nodes: TopologyNode[];
  edges: TopologyEdge[];
  node_count: number;
  edge_count: number;
}

export interface NodeCpuMetric {
  node_id: string;
  node_name: string;
  cpu_usage: number;
}

export interface CpuMetricsResponse {
  metrics: NodeCpuMetric[];
  average_cpu: number;
}

export interface PacketLatencyMetric {
  packet_id: string;
  sequence: number;
  source_node_id: string;
  destination_node_id: string;
  latency: number;
}

export interface LatencyMetricsResponse {
  metrics: PacketLatencyMetric[];
  average_latency: number;
  min_latency: number;
  max_latency: number;
}

export interface StatisticsResponse {
  total_nodes: number;
  total_links: number;
  total_packets: number;
  total_sent: number;
  total_received: number;
  total_dropped: number;
  delivery_rate_percent: number;
}

export interface HealthResponse {
  status: string;
  app_name: string;
  version: string;
}

export interface AnimatedPacket {
  id: string;
  sourceId: string;
  destinationId: string;
  path: string[];
  status: PacketStatus;
  dropReason?: DropReason | null;
  progress: number; // 0.0 to 1.0
  currentHopIndex: number;
  payload: string;
  latency: number;
  color: string;
}
