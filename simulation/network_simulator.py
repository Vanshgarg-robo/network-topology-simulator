from models.node import Node
from models.packet import Packet
from models.link import Link
from collections import defaultdict, deque
from simulation.packet_simulator import PacketSimulator
from simulation.cpu_simulator import CPUSimulator

class NetworkSimulator:

    def __init__(self):

        self.nodes = {}
        self.packets = []
        self.packet_counter = 0
        self.links = [
            Link("A", "B"),
            Link("B", "E"),
            Link("C", "D"),
            Link("D", "E"),
            Link("A", "E"),
            Link("B", "D"),
            Link("C", "A"),
        ]
        self.graph = defaultdict(list)
        self.build_graph()

        self.packet_simulator = PacketSimulator()
        self.cpu_simulator = CPUSimulator()

        self.total_sent = 0
        self.total_received = 0
        self.total_dropped = 0
        self.total_packets = 0

    def add_node(self, node_name):
        if node_name not in self.nodes:
            node = Node(node_name)
            self.nodes[node_name] = node
            #(f"{node_name} created")

    def disable_node(self, node_name):

        if node_name in self.nodes:
            self.nodes[node_name].status = "offline"
            print(f"{node_name} disabled")

    def enable_node(self, node_name):

        if node_name in self.nodes:
            self.nodes[node_name].status = "online"
            print(f"{node_name} enabled")

    def build_graph(self):
        self.graph = defaultdict(list)
        for link in self.links:
            if link.status == "active":
                self.graph[link.source].append(link.destination)
                self.graph[link.destination].append(link.source)

    def create_link(self, source, destination):

        link_node = Link(source, destination)
        self.links.append(link_node)
        print(f"Link created: {source} ---> {destination}")
        self.build_graph()

    def link_exists(self, source, destination):
        return self.find_path(source, destination) is not None

    def disable_link(self, source, destination):
        for link in self.links:
            if ( link.source==source) and (link.destination==destination ):
                link.status = "down"
                self.build_graph()
                print(f"Link {source}->{destination} disabled")
                return
        print("Link not found")

    def enable_link(self, source, destination):
        for link in self.links:
            if (link.source==source) and (link.destination==destination):
                link.status = "active"
                self.build_graph()
                print(f"Link {source}->{destination} enabled")
                return
        print("Link not found")

    def find_path(self, source, destination):
        queue = deque([[source]])
        visited = set()
        while queue:
            path = queue.popleft()
            current_node = path[-1]
            if current_node == destination:
                return path
            if current_node not in visited:
                visited.add(current_node)
                for neighbour in self.graph[current_node]:
                    new_path = list(path)
                    new_path.append(neighbour)
                    queue.append(new_path)

        return None

    def create_packet(self, source, destination, payload):
        self.packet_counter += 1
        return Packet(self.packet_counter, source, destination, payload)

    def send_packet(self, source, destination, payload):
        if source not in self.nodes:
            self.add_node(source)
        if destination not in self.nodes:
            self.add_node(destination)

        packet = self.create_packet(source, destination, payload)
        self.packets.append(packet)

        if self.nodes[source].status == "offline":
            packet.status = "dropped"
            packet.reason = "SOURCE_OFFLINE"
            self.total_dropped += 1
            self.total_packets += 1
            return

        if self.nodes[destination].status == "offline":
            packet.status = "dropped"
            packet.reason = "DESTINATION_OFFLINE"
            self.total_dropped += 1
            self.total_packets += 1
            return

        path = self.find_path(source, destination)
        if path:
            packet.status = "delivered"
            packet.path = path

            self.packet_simulator.transmit(packet, source, destination)

            for node_name in path:
                self.cpu_simulator.update_node_cpu(self.nodes[node_name])

            self.total_sent += 1
            self.total_received += 1
            self.total_packets += 1
        else:
            packet.status = "dropped"
            packet.reason = "NO_ROUTE"
            self.total_dropped += 1
            self.total_packets += 1

    def delivery_rate(self):
        if self.total_packets == 0:
            return 0
        return (self.total_received/ self.total_packets) * 100

    def show_nodes(self):
        for node in self.nodes.values():
            print(node)

    def show_links(self):
        for link in self.links:
            print(link)

    def show_packets(self):
        for packet in self.packets:
            print(packet)

    def show_stats(self):
        print(f"Nodes : {len(self.nodes)}")
        print(f"Links : {len(self.links)}")

        print(f"\nSent : {self.total_sent}")
        print(f"Received : {self.total_received}")
        print(f"Dropped : {self.total_dropped}")
        print(f"Packets : {self.total_packets}")

        delivery_rate = self.delivery_rate()
        print(f"\nDelivery Rate : {delivery_rate:.2f}%")