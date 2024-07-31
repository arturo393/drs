import time
import socket

from typing import  Union
from src.plugins.drs.definitions.transceiver.transceiver import Transceiver


class TCPTransceiver(Transceiver):
    """Transceiver for communicating over TCP."""

    tcp_port = 65050

    def transmit_and_receive(self, commands: list, **kwargs) -> Union[dict, int]:
        """Transmits commands over TCP and receives responses."""
        address = kwargs.get("address")

        rt = time.time()
        reply_counter = 0
        for message in commands:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((address, self.tcp_port))
                    sock.settimeout(2)
                    sock.sendall(message.get_command_query_as_bytearray())
                    data_received = sock.recv(1024)
                    sock.close()
                    if message.save_if_valid(data_received):
                        reply_counter = reply_counter + 1
                    time.sleep(0.1)
            except Exception:
                return 0

        rt = str(time.time() - rt)
        return {"rt": rt, "reply_counter": reply_counter}