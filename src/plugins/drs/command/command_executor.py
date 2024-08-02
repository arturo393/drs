import os
import sys

from ..definitions.nagios import CRITICAL, OK
from ..command.command import Command
from ..transceiver.serial_transceiver import SerialTransceiver
from ..transceiver.tcp_transceiver import TCPTransceiver


class CommandExecutor:
    def __init__(self, args):
        self.args = args
        self.command = Command(args=self.args)

    def execute(self, cmd_type):
        # Create command

        # Transmit and receive

        try:
            device = self.command.parameters.get("device")
            address = self.command.parameters.get("address")


            tcp_transceiver = TCPTransceiver(address, 65050, 65053)
            reply_counter = 0
            for command_protocol in self.command.commands:





                reply_frame = tcp_transceiver.get_reply(command_protocol.get_command_query_as_bytearray())
                data = command_protocol.get_value(reply_frame)
                if data:
                    self.command.parameters.update(data)

            result = {"rt": "1", "reply_counter": reply_counter}
            self.command.parameters.update(result)
            if isinstance(result, int) and not result:
                return CRITICAL, self._print_error(address)

        except Exception as e:
            return CRITICAL, f"Error: {e}"

    def get_command(self):
        return self.command

    def _check_critical(self, exit_code, message):
        if exit_code == CRITICAL:
            self._exit_critical(message)

    @staticmethod
    def _exit_critical(message: object) -> object:
        sys.stderr.write(f"CRITICAL - {message}")
        sys.exit(CRITICAL)

    def _print_error(self, address):
        pass
