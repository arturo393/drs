import time
import socket

from typing import Union
from src.plugins.drs.definitions.transceiver.transceiver import Transceiver


class TCPTransceiver(Transceiver):
    """Transceiver for communicating over TCP."""

    def __init__(self, address, tcp_port, udp_port):
        self._address = address
        self._tcp_port = tcp_port
        self._udp_port = udp_port

    def get_reply(self, query_frame: bytearray) -> bytearray:
        return self._transmit_and_receive_socket(query_frame)

    def transmit_and_receive(self, commands: list, **kwargs) -> Union[dict, int]:
        """Transmits commands over TCP and receives responses."""
        address = kwargs.get("address")

        rt = time.time()
        reply_counter = 0
        for message in commands:
            reply_frame = self._transmit_and_receive_socket(message.get_command_query_as_bytearray())
            time.sleep(0.1)
            if message.save_if_valid(reply_frame):
                reply_counter = reply_counter + 1

        rt = str(time.time() - rt)
        return {"rt": rt, "reply_counter": reply_counter}

    def _transmit_and_receive_socket(self, query_frame) -> bytearray:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self._address, self._tcp_port))
                sock.settimeout(2)
                sock.sendall(query_frame)
                data_received = sock.recv(1024)
                sock.close()
        except Exception:
            data_received = bytearray()

        return data_received
