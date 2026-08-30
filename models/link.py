class Link:

    def __init__(self, source, destination):
        self.source = source
        self.destination = destination
        self.status = "active"

    def __repr__(self):
        return (
            f"Link("
            f"{self.source}->{self.destination}, "
            f"status={self.status})"
        )