from matplotlib.figure import Figure
import networkx as nx
from matplotlib.lines import Line2D

def cpu_chart(simulator):

    figure = Figure(figsize=(5, 3))
    ax = figure.add_subplot(111)
    node_names = []
    cpu_values = []

    for name in sorted(simulator.nodes):
        node = simulator.nodes[name]
        node_names.append(node.name)
        cpu_values.append(node.cpu_usage)

    ax.bar(node_names, cpu_values)
    ax.set_title("CPU Usage")
    ax.set_xlabel("Nodes")
    ax.set_ylabel("CPU %")

    return figure

def latency_chart(simulator):

    figure = Figure(figsize=(5, 3))

    ax = figure.add_subplot(111)

    packet_ids = []
    latencies = []

    for packet in simulator.packets:

        if packet.status == "delivered":
            packet_ids.append(packet.packet_id)
            latencies.append(packet.latency)

    ax.plot(packet_ids, latencies, marker="o")

    ax.set_title("Packet Latency")
    ax.set_xlabel("Packet ID")
    ax.set_ylabel("Latency (ms)")

    return figure

def topology_chart(simulator):
    G = nx.Graph()
    for link in simulator.links:
        if link.status == "active":
            G.add_edge(link.source,link.destination)

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)
    ax.set_title("Network Topology")

    legend_elements = [
        Line2D([0], [0], marker='o', color='w',
               label='Online',
               markerfacecolor='green',
               markersize=10),

        Line2D([0], [0], marker='o', color='w',
               label='Offline',
               markerfacecolor='red',
               markersize=10)
    ]

    ax.legend(handles=legend_elements)

    node_colors = []
    for node in G.nodes():
        if simulator.nodes[node].status == "online":
            node_colors.append("green")
        else:
            node_colors.append("red")
    nx.draw(G, ax=ax, with_labels=True, node_color=node_colors)

    return fig