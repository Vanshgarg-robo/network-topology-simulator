from simulation.network_simulator import NetworkSimulator
import json
from gui.main_window import MainWindow

def load_data():
    with open('packets.json','r') as f:
        data     = json.load(f)
    return data

sim = NetworkSimulator()

data = load_data()

sim.add_node("E")
sim.disable_node("E")
print(sim.nodes["E"])

for packet in data:
    sim.send_packet(packet["source"], packet["destination"], packet["payload"])

gui = MainWindow(sim)
gui.run()
