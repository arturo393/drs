class DRU:
    def __init__(self, position, port, device_id, master_hostname, ip_addr, parent):
        self.position = position
        self.port = port
        self.device_id = device_id
        self.hostname = f"dru{device_id}"
        self.master_hostname = master_hostname
        self.ip_addr = ip_addr
        self.parent = parent
        self.name = f"Remote {port}{position}"
        self.comm_type = ""

    def __repr__(self):
        return "DRU()"

    def __str__(self):
        response = ""
        response += f"RU{self.port}{self.position} "
        response += f"hostname: {self.hostname} "
        response += f"ip_addr: {self.ip_addr} "
        return response

    def __eq__(self, other):
        return self.position == other.position and self.port == other.position

