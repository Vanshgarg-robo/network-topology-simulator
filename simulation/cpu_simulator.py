import random

class CPUSimulator:
    def generate_cpu(self, node):
        if node.status == "offline":
            return 0
        return random.randint(5, 30)

    def update_node_cpu(self, node):
        node.cpu_usage = self.generate_cpu(node)