class Packet:

    def __init__(self, packet_id, source, destination, payload):
        self.packet_id = packet_id
        self.source = source
        self.destination = destination
        self.payload = payload
        self.status = "created"
        self.reason = None
        self.path = []
        self.latency = 0

    def __str__(self):
        route = " -> ".join(self.path) if self.path else "N/A"

        return (
            f"<Packet id={self.packet_id} "
            f"{self.source}->{self.destination} "
            f"payload='{self.payload}' "
            f"status={self.status} "
            f"reason={self.reason} "
            f"path={route} "
            f"latency={self.latency}ms>"
        )