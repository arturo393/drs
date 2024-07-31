import abc
import time
import serial
import sys
from typing import Union
from src.plugins.drs.definitions.nagios import CRITICAL
from src.plugins.drs.definitions.transceiver.transceiver import Transceiver


class SerialTransceiver(Transceiver):
    """Transceiver for communicating over a serial port."""

    @staticmethod
    def _set_serial_with_timeout(
        port: str, baudrate: int, timeout: int
    ) -> serial.Serial:
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

    def transmit_and_receive(self, commands: list, **kwargs) -> Union[dict, int]:
        """Transmits commands over the serial port and receives responses."""
        port = kwargs.get("port")
        baud = kwargs.get("baud")
        timeout = kwargs.get("timeout", 6)  # Default timeout

        try:
            rt = time.time()
            serial_conn = self._set_serial_with_timeout(port, baud, timeout)

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
                    if self._is_valid_reply(cmd_name):
                        cmd_number_ok += 1
                        break
                    serial_conn.write(cmd_name.query_bytes)
                    retry += 1
                    if retry == 3:
                        break
            serial_conn.close()
            rt = time.time() - rt
            return {"rt": rt, "cmd_number_ok": cmd_number_ok}

        except serial.SerialException:
            sys.stderr.write(
                f"CRITICAL - The specified port {port} is not available at {baud}\n"
            )
            sys.exit(CRITICAL)

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


