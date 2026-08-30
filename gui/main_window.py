import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from gui.charts import cpu_chart ,latency_chart, topology_chart
import random

class MainWindow:

    def __init__(self, simulator):

        self.simulator = simulator

        self.root = tk.Tk()
        self.root.title("Network Simulator")
        self.root.geometry("1400x900")

        self.create_widgets()

    def create_widgets(self):

        # Title
        title = tk.Label(self.root, text="Network Simulator", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        toolbar = tk.Frame(self.root)
        toolbar.pack(fill="x", pady=5)
        tk.Button(
            toolbar,
            text="Refresh",
            command=self.refresh_data
        ).pack(side="left", padx=5)

        # Top Frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill="both", expand=True)

        # Nodes
        self.node_box = tk.Listbox(top_frame, width=40)
        self.node_box.pack(side="left", fill="both", expand=True)

        # Links
        self.link_box = tk.Listbox(top_frame, width=40)
        self.link_box.pack(side="left", fill="both", expand=True)

        # Stats
        self.stats_box = tk.Text(top_frame,width=40,height=10)
        self.stats_box.pack(side="left",fill="both",expand=True)


        # -------------------
        # CHART FRAME
        # -------------------

        self.chart_frame = tk.Frame(self.root)
        self.chart_frame.pack(fill="both", expand=True)

        # CPU Chart
        self.cpu_figure = cpu_chart(self.simulator)
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_figure, master=self.chart_frame)
        self.cpu_canvas.draw()
        self.cpu_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

        # Latency Chart
        self.latency_figure = latency_chart(self.simulator)
        self.latency_canvas = FigureCanvasTkAgg(self.latency_figure, master=self.chart_frame)
        self.latency_canvas.draw()
        self.latency_canvas.get_tk_widget().pack( side="right", fill="both", expand=True)

        # Topology Chart
        self.topology_figure = topology_chart(self.simulator)
        self.topology_canvas = FigureCanvasTkAgg(self.topology_figure, master=self.chart_frame)
        self.topology_canvas.draw()
        self.topology_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)


        # -------------------
        # PACKET FRAME
        # -------------------


        packet_frame = tk.Frame(self.root)
        packet_frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(packet_frame)
        scrollbar.pack(side="right", fill="y")
        self.packet_box = tk.Text(packet_frame, yscrollcommand=scrollbar.set)
        self.packet_box.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.packet_box.yview)

        self.load_data()

    def load_data(self):
        self.node_box.delete(0, tk.END)
        self.link_box.delete(0, tk.END)

        self.stats_box.delete("1.0", tk.END)
        self.packet_box.delete("1.0", tk.END)

        # Nodes
        for name in sorted(self.simulator.nodes):
            node = self.simulator.nodes[name]
            self.node_box.insert("end",str(node))

        # Stats
        stats = (
            f"Nodes : {len(self.simulator.nodes)}\n"
            f"Links : {len(self.simulator.links)}\n\n"
            f"Sent : {self.simulator.total_sent}\n"
            f"Received : {self.simulator.total_received}\n"
            f"Dropped : {self.simulator.total_dropped}\n"
            f"Packets : {self.simulator.total_packets}\n\n"
            f"Delivery Rate : {self.simulator.delivery_rate():.2f}%"
        )


        # Links
        for link in self.simulator.links:
            self.link_box.insert("end", str(link))

        self.stats_box.insert("1.0", stats)

        # Packets
        for packet in self.simulator.packets:
            self.packet_box.insert("end", str(packet) + "\n")

    def redraw_charts(self):

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        self.cpu_figure = cpu_chart(self.simulator)
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_figure, master=self.chart_frame)
        self.cpu_canvas.draw()
        self.cpu_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

        self.topology_figure = topology_chart(self.simulator)
        self.topology_canvas = FigureCanvasTkAgg(self.topology_figure, master=self.chart_frame)
        self.topology_canvas.draw()
        self.topology_canvas.get_tk_widget().pack(side="left", fill="both", expand=True)

        self.latency_figure = latency_chart(self.simulator)
        self.latency_canvas = FigureCanvasTkAgg(self.latency_figure, master=self.chart_frame)
        self.latency_canvas.draw()
        self.latency_canvas.get_tk_widget().pack(side="right", fill="both", expand=True)

    def refresh_data(self):
        for node in self.simulator.nodes.values():

            if node.status == "online":
                node.cpu_usage = random.randint(5, 40)
            else:
                node.cpu_usage = 0

        for packet in self.simulator.packets:
            if packet.status == "delivered":
                packet.latency = random.randint(10, 100)

        self.load_data()
        self.redraw_charts()

    def run(self):
        self.root.mainloop()
