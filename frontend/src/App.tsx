import React, { useEffect, useRef, useState } from 'react';
import { api } from './services/api';
import {
  AnimatedPacket,
  CpuMetricsResponse,
  LatencyMetricsResponse,
  LinkItem,
  NodeItem,
  PacketItem,
  StatisticsResponse,
} from './types/api';
import { Header } from './components/Header';
import { NetworkGraph } from './components/NetworkGraph';
import { PacketSender } from './components/PacketSender';
import { TelemetryHud } from './components/TelemetryHud';
import { PacketLog } from './components/PacketLog';
import { NodeModal } from './components/NodeModal';
import { LinkModal } from './components/LinkModal';
import { TopologyPresets } from './components/TopologyPresets';

export const App: React.FC = () => {
  // Global Data State
  const [nodes, setNodes] = useState<NodeItem[]>([]);
  const [links, setLinks] = useState<LinkItem[]>([]);
  const [packets, setPackets] = useState<PacketItem[]>([]);
  const [cpuMetrics, setCpuMetrics] = useState<CpuMetricsResponse | null>(null);
  const [latencyMetrics, setLatencyMetrics] = useState<LatencyMetricsResponse | null>(null);
  const [stats, setStats] = useState<StatisticsResponse | null>(null);
  const [serverOnline, setServerOnline] = useState<boolean>(false);

  // Active packet animations in progress on canvas
  const [activePackets, setActivePackets] = useState<AnimatedPacket[]>([]);

  // UI Modals
  const [isNodeModalOpen, setIsNodeModalOpen] = useState(false);
  const [isLinkModalOpen, setIsLinkModalOpen] = useState(false);
  const [isPresetsOpen, setIsPresetsOpen] = useState(false);

  // Loading States
  const [isSending, setIsSending] = useState(false);
  const [isAutoTraffic, setIsAutoTraffic] = useState(false);

  const autoTrafficTimerRef = useRef<number | null>(null);

  // Sync state from FastAPI backend
  const fetchData = async () => {
    try {
      await api.getHealth();
      setServerOnline(true);

      const [nodeList, linkList, packetList, cpuData, latencyData, statData] = await Promise.all([
        api.getNodes(),
        api.getLinks(),
        api.getPackets(),
        api.getCpuMetrics(),
        api.getLatencyMetrics(),
        api.getStatistics(),
      ]);

      setNodes(nodeList);
      setLinks(linkList);
      setPackets(packetList);
      setCpuMetrics(cpuData);
      setLatencyMetrics(latencyData);
      setStats(statData);
    } catch (err) {
      console.error('Telemetry fetch error:', err);
      setServerOnline(false);
    }
  };

  // Initial load and periodic telemetry poll
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2500);
    return () => clearInterval(interval);
  }, []);

  // Animation frame ticker to progress in-transit animated packets along links
  useEffect(() => {
    if (activePackets.length === 0) return;

    const animInterval = setInterval(() => {
      setActivePackets((prev) => {
        const next: AnimatedPacket[] = [];

        prev.forEach((pkt) => {
          if (!pkt.path || pkt.path.length < 2) {
            // Single hop / dropped packet, age it out
            if (pkt.progress < 1) {
              next.push({ ...pkt, progress: pkt.progress + 0.05 });
            }
            return;
          }

          const totalHops = pkt.path.length - 1;
          const newProgress = pkt.progress + 0.04;

          if (newProgress >= 1.0) {
            // Completed current hop
            const nextHopIndex = pkt.currentHopIndex + 1;
            if (nextHopIndex < totalHops) {
              next.push({
                ...pkt,
                currentHopIndex: nextHopIndex,
                progress: 0.0,
              });
            }
            // If finished all hops, it drops out of the active list
          } else {
            next.push({ ...pkt, progress: newProgress });
          }
        });

        return next;
      });
    }, 20);

    return () => clearInterval(animInterval);
  }, [activePackets.length]);

  // Send packet action
  const handleSendPacket = async (sourceId: string, destId: string, payload: string) => {
    try {
      setIsSending(true);
      const packet = await api.sendPacket(sourceId, destId, payload);

      // Trigger visual particle animation
      setActivePackets((prev) => [
        ...prev,
        {
          id: packet.id,
          sourceId,
          destinationId: destId,
          path: packet.path || [],
          status: packet.status,
          dropReason: packet.drop_reason,
          progress: 0.0,
          currentHopIndex: 0,
          payload: packet.payload,
          latency: packet.latency,
          color: packet.status === 'delivered' ? '#00f5a0' : '#ff4b72',
        },
      ]);

      await fetchData();
    } catch (err: any) {
      alert(`Packet error: ${err.message}`);
    } finally {
      setIsSending(false);
    }
  };

  // Node & Link State Toggles (Failure simulation)
  const handleToggleNode = async (id: string, currentStatus: string) => {
    try {
      if (currentStatus === 'online') {
        await api.disableNode(id);
      } else {
        await api.enableNode(id);
      }
      await fetchData();
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleToggleLink = async (id: string, currentStatus: string) => {
    try {
      if (currentStatus === 'active') {
        await api.disableLink(id);
      } else {
        await api.enableLink(id);
      }
      await fetchData();
    } catch (err: any) {
      console.error(err);
    }
  };

  const handleDeleteNode = async (id: string) => {
    try {
      await api.deleteNode(id);
      await fetchData();
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
  };

  const handleDeleteLink = async (id: string) => {
    try {
      await api.deleteLink(id);
      await fetchData();
    } catch (err: any) {
      alert(`Delete error: ${err.message}`);
    }
  };

  const handleCreateLink = async (sourceId: string, destId: string) => {
    try {
      await api.createLink(sourceId, destId);
      await fetchData();
    } catch (err: any) {
      alert(`Link error: ${err.message}`);
    }
  };

  const handleCreateNode = async (name: string) => {
    await api.createNode(name);
    await fetchData();
  };

  // Auto Traffic Simulator (Streams packets randomly)
  useEffect(() => {
    if (isAutoTraffic) {
      autoTrafficTimerRef.current = window.setInterval(() => {
        if (nodes.length < 2) return;
        const onlineNodes = nodes.filter((n) => n.status === 'online');
        if (onlineNodes.length < 2) return;

        const shuffled = [...onlineNodes].sort(() => 0.5 - Math.random());
        const s = shuffled[0];
        const d = shuffled[1];

        handleSendPacket(s.id, d.id, `Telemetry Stream [${new Date().toLocaleTimeString()}]`);
      }, 1500);
    } else {
      if (autoTrafficTimerRef.current) {
        clearInterval(autoTrafficTimerRef.current);
      }
    }

    return () => {
      if (autoTrafficTimerRef.current) {
        clearInterval(autoTrafficTimerRef.current);
      }
    };
  }, [isAutoTraffic, nodes]);

  // Chaos Mode (Randomly break/restore links and nodes)
  const handleTriggerChaos = async () => {
    if (links.length === 0 && nodes.length === 0) return;

    if (Math.random() > 0.5 && links.length > 0) {
      const randLink = links[Math.floor(Math.random() * links.length)];
      await handleToggleLink(randLink.id, randLink.status);
    } else if (nodes.length > 0) {
      const randNode = nodes[Math.floor(Math.random() * nodes.length)];
      await handleToggleNode(randNode.id, randNode.status);
    }
  };

  // Preset Topologies Loader
  const handleApplyPreset = async (preset: 'mesh' | 'ring' | 'star' | 'tree' | 'default') => {
    try {
      // 1. Clear existing links and nodes
      for (const link of links) {
        await api.deleteLink(link.id);
      }
      for (const node of nodes) {
        await api.deleteNode(node.id);
      }

      // 2. Build preset topology
      if (preset === 'default') {
        const a = await api.createNode('Node-A');
        const b = await api.createNode('Node-B');
        const c = await api.createNode('Node-C');
        const d = await api.createNode('Node-D');
        const e = await api.createNode('Node-E');

        await api.createLink(a.id, b.id);
        await api.createLink(b.id, e.id);
        await api.createLink(a.id, c.id);
        await api.createLink(c.id, d.id);
        await api.createLink(b.id, d.id);
        await api.createLink(d.id, e.id);
      } else if (preset === 'mesh') {
        const n1 = await api.createNode('Core-1');
        const n2 = await api.createNode('Core-2');
        const n3 = await api.createNode('Core-3');
        const n4 = await api.createNode('Core-4');
        const nodeList = [n1, n2, n3, n4];

        for (let i = 0; i < nodeList.length; i++) {
          for (let j = i + 1; j < nodeList.length; j++) {
            await api.createLink(nodeList[i].id, nodeList[j].id);
          }
        }
      } else if (preset === 'ring') {
        const r1 = await api.createNode('Ring-1');
        const r2 = await api.createNode('Ring-2');
        const r3 = await api.createNode('Ring-3');
        const r4 = await api.createNode('Ring-4');
        const r5 = await api.createNode('Ring-5');

        await api.createLink(r1.id, r2.id);
        await api.createLink(r2.id, r3.id);
        await api.createLink(r3.id, r4.id);
        await api.createLink(r4.id, r5.id);
        await api.createLink(r5.id, r1.id);
      } else if (preset === 'star') {
        const hub = await api.createNode('Hub-Core');
        const s1 = await api.createNode('Spoke-1');
        const s2 = await api.createNode('Spoke-2');
        const s3 = await api.createNode('Spoke-3');
        const s4 = await api.createNode('Spoke-4');

        await api.createLink(hub.id, s1.id);
        await api.createLink(hub.id, s2.id);
        await api.createLink(hub.id, s3.id);
        await api.createLink(hub.id, s4.id);
      } else if (preset === 'tree') {
        const root = await api.createNode('Root');
        const dist1 = await api.createNode('Dist-1');
        const dist2 = await api.createNode('Dist-2');
        const acc1 = await api.createNode('Access-1');
        const acc2 = await api.createNode('Access-2');

        await api.createLink(root.id, dist1.id);
        await api.createLink(root.id, dist2.id);
        await api.createLink(dist1.id, acc1.id);
        await api.createLink(dist2.id, acc2.id);
      }

      await fetchData();
    } catch (err: any) {
      alert(`Preset error: ${err.message}`);
    }
  };

  return (
    <div style={{ maxWidth: '1600px', margin: '0 auto', paddingBottom: '30px' }}>
      {/* Top Header */}
      <Header
        stats={stats}
        serverOnline={serverOnline}
        onRefresh={fetchData}
        onOpenAddNode={() => setIsNodeModalOpen(true)}
        onOpenAddLink={() => setIsLinkModalOpen(true)}
        onOpenPresets={() => setIsPresetsOpen(true)}
        isAutoTraffic={isAutoTraffic}
        onToggleAutoTraffic={() => setIsAutoTraffic(!isAutoTraffic)}
      />

      {/* Main Grid Layout */}
      <main
        style={{
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) 380px',
          gap: '20px',
          padding: '0 20px',
        }}
      >
        {/* Left Column: Interactive Topology Graph & Sender & Logs */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Network Graph Visualizer */}
          <NetworkGraph
            nodes={nodes}
            links={links}
            activePackets={activePackets}
            onToggleNode={handleToggleNode}
            onToggleLink={handleToggleLink}
            onDeleteNode={handleDeleteNode}
            onDeleteLink={handleDeleteLink}
            onCreateLink={handleCreateLink}
          />

          {/* Controls & Packet Sender */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <PacketSender
              nodes={nodes}
              onSendPacket={handleSendPacket}
              onTriggerChaos={handleTriggerChaos}
              isLoading={isSending}
            />
            <PacketLog packets={packets} nodes={nodes} />
          </div>
        </div>

        {/* Right Column: Telemetry HUD & Diagnostics */}
        <div>
          <TelemetryHud
            cpuMetrics={cpuMetrics}
            latencyMetrics={latencyMetrics}
            stats={stats}
          />
        </div>
      </main>

      {/* Modals */}
      <NodeModal
        isOpen={isNodeModalOpen}
        onClose={() => setIsNodeModalOpen(false)}
        onSubmit={handleCreateNode}
      />

      <LinkModal
        isOpen={isLinkModalOpen}
        nodes={nodes}
        onClose={() => setIsLinkModalOpen(false)}
        onSubmit={handleCreateLink}
      />

      <TopologyPresets
        isOpen={isPresetsOpen}
        onClose={() => setIsPresetsOpen(false)}
        onApplyPreset={handleApplyPreset}
        isLoading={isSending}
      />
    </div>
  );
};

export default App;
