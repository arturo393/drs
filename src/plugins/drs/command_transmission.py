import time
from ctypes import Union
from typing import Any

import serial
import socket
import sys


from src.plugins.drs.definitions.nagios import WARNING, CRITICAL, OK, UNKNOWN


class CommandTransmission:
    """Handles the transmission of commands over different protocols (TCP, Serial)."""

    tcp_port = 65050
    master_to_rs485_udp_port = 65055
    remote_to_rs485_udp_port = 65053

    @staticmethod
    def _transmit_tcp(commands: list, address: str) -> dict[str, str | int | Any]:
        """Transmits commands over TCP and returns the received data."""
        rt = time.time()
        reply_counter = 0
        for message in commands:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((address, CommandTransmission.tcp_port))
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

    @staticmethod
    def _transmit_serial(commands: list, port: str, baud: int, timeout: int = 6):
        """Transmits commands over a serial connection and returns the received data."""
        try:
            rt = time.time()
            serial_conn = CommandTransmission._set_serial_with_timeout(
                port, baud, timeout=timeout
            )
        except serial.SerialException:
            sys.stderr.write(
                f"CRITICAL - The specified port {port} is not available at {baud}\n"
            )
            sys.exit(CRITICAL)

        cmd_number_ok = 0
        for cmd_name in commands:
            cmd_name.query_bytes = bytearray.fromhex(cmd_name.query)
            serial_conn.write(cmd_name.query_bytes)
            serial_conn.flush()
            cmd_name.reply_bytes = b""
            retry = 0
            while True:
                cmd_name.reply_bytes = serial_conn.read(200)
                cmd_name.reply = cmd_name.reply_bytes.hex()
                if CommandTransmission._is_valid_reply(cmd_name):
                    cmd_number_ok += 1
                    break
                serial_conn.write(cmd_name.query_bytes)
                retry += 1
                if retry == 3:
                    break
        serial_conn.close()
        rt = time.time() - rt
        return {"rt": rt, "cmd_number_ok": cmd_number_ok}

    @staticmethod
    def _is_valid_reply(cmd_name) -> bool:
        """Validates the received serial reply."""
        start_index = 0
        id_index = 7
        cmd_code_index = 15
        if cmd_name.reply_bytes == b"":
            return False
        if len(cmd_name.query_bytes) != len(cmd_name.reply_bytes):
            return False
        if (
            cmd_name.query_bytes[start_index]
            != cmd_name.reply_bytes[start_index]
        ):
            return False
        if cmd_name.query_bytes[id_index] != cmd_name.reply_bytes[id_index]:
            return False
        if (
            cmd_name.query_bytes[cmd_code_index]
            != cmd_name.reply_bytes[cmd_code_index]
        ):
            return False
        if (
            cmd_name.query_bytes[cmd_code_index + 1]
            != cmd_name.reply_bytes[cmd_code_index + 1]
        ):
            return False
        return True

    @staticmethod
    def _set_serial_with_timeout(port: str, baudrate: int, timeout: int) -> serial.Serial:
        """Establishes a serial connection with timeout and error handling."""
        for times in range(3):
            try:
                s = serial.Serial(port, baudrate)
                s.timeout = timeout
                s.exclusive = True
                return s

            except serial.SerialException as e:
                time.sleep(1)
                if times == 2:
                    sys.stderr.write(
                        "CRITICAL - " + (e.args.__str__()) + str(port) + "\n"
                    )
                    sys.exit(CRITICAL)