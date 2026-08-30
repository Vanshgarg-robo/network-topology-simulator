from simulation.latency_simulator import LatencySimulator

class PacketSimulator:
    def __init__(self):
        self.latency_simulator = LatencySimulator()

    def transmit(self, packet, source, destination):
        packet.latency = (self.latency_simulator.calculate_latency(source, destination))