class Node:

    def __init__(self, name):
        self.name = name
        self.status = "online"
        self.cpu_usage = 0

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return (
            f"Node("
            f"{self.name}, "
            f"status={self.status}, "
            f"cpu={self.cpu_usage}%"
            f")"
        )