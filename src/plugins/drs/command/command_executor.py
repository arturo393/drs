import sys

from src.plugins.drs.definitions.nagios import CRITICAL
from src.plugins.drs.command.command import Command


class CommandExecutor:
    def __init__(self, args):
        self.args = args
        self.command = Command(args=self.args)

    def execute(self, cmd_type):
        # Create command

        # Transmit and receive
        exit_code, message = self.command.transmit_and_receive()
        self._check_critical(exit_code, message)

        # Extract and decode
        if not self.command.extract_and_decode_received():
            self._exit_critical("No decoded data")

    def get_command(self):
        return self.command

    def _check_critical(self, exit_code, message):
        if exit_code == CRITICAL:
            self._exit_critical(message)

    def _exit_critical(self, message):
        sys.stderr.write(f"CRITICAL - {message}")
        sys.exit(CRITICAL)
