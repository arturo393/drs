import os
import sys

from typing import Optional
from typing import Tuple

from src.plugins.drs.command.command_factory import CommandFactory
from src.plugins.drs.command_transmission import CommandTransmission
from src.plugins.drs.definitions.nagios import WARNING, CRITICAL, OK, UNKNOWN


class Command:
    """
    Represents a command to be sent to a device.
    Handles command creation, transmission, and response reception.
    """

    def __init__(self, args: dict):
        self.cmd_number_ok = None
        self.parameters = {}
        self.set_args(args)
        self.message_type = None
        self._optical_port = self.parameters.get("optical_port")
        self._remote_position = self.parameters.get("device_number")

        # Extract parameters for clarity and conciseness
        device = self.parameters.get("device")
        cmd_name = self.parameters.get("cmd_name")
        cmd_type = self.parameters.get("cmd_type")

        # Use a dictionary to map command types to creation methods
        command_creators = {
            "group_query": CommandFactory.create_group_query_commands,
            "single_set": CommandFactory.create_single_command,
            "single_query": CommandFactory.create_single_command,
        }

        # Create commands using the appropriate creation method based on command type
        create_command = command_creators.get(cmd_type)
        if create_command:
            if cmd_type == "group_query":
                self.commands = create_command(
                    self._get_remote_tree_id(), device
                )
            else:
                self.commands = create_command(
                    self._get_remote_tree_id(), cmd_name
                )
        else:
            self.commands = (
                None  # Or handle the unknown command type appropriately
            )

    def set_args(self, args: dict) -> None:
        """Sets the parameters for the command from the provided arguments."""
        self.parameters["address"] = args["address"]
        self.parameters["device"] = args["device"]
        self.parameters["hostname"] = args["hostname"]
        self.parameters["cmd_type"] = args["cmd_type"]
        self.parameters["cmd_data"] = args["cmd_data"]

        if isinstance(args["cmd_name"], str):
            if len(args["cmd_name"]) < 4:
                self.parameters["cmd_name"] = int(args["cmd_name"])
            if len(args["cmd_name"]) == 4:
                self.parameters["cmd_name"] = int(args["cmd_name"], 16)

        self.parameters["cmd_body_length"] = int(args["cmd_body_length"])
        self.parameters["device_number"] = int(args["device_number"])
        self.parameters["optical_port"] = int(args["optical_port"])
        self.parameters["work_bandwidth"] = int(args["bandwidth"])
        self.parameters["warning_uplink_threshold"] = int(
            args["warning_uplink_threshold"]
        )
        self.parameters["critical_uplink_threshold"] = int(
            args["critical_uplink_threshold"]
        )
        self.parameters["warning_downlink_threshold"] = int(
            args["warning_downlink_threshold"]
        )
        self.parameters["critical_downlink_threshold"] = int(
            args["critical_downlink_threshold"]
        )
        self.parameters["warning_temperature_threshold"] = int(
            args["warning_temperature_threshold"]
        )
        self.parameters["critical_temperature_threshold"] = int(
            args["critical_temperature_threshold"]
        )

        opt, dru = self._decode_address(self.parameters["address"])
        self.parameters["device_number"] = dru
        self.parameters["optical_port"] = opt
        self.parameters["baud_rate"] = int(args["baud_rate"])

    def _get_remote_tree_id(self) -> str:
        """Returns the remote tree ID."""
        return f"{self._optical_port}{self._remote_position}"

    def _decode_address(self, address: str) -> Optional[Tuple[int, int]]:
        """
        Decodes the address string provided in the configuration and returns a tuple of (opt, dru) values.

        Args:
            address (str): The address string to decode.

        Returns:
            Optional[Tuple[int, int]]: A tuple containing the decoded opt and dru values, or None if the address format is invalid.
        """

        if not address.startswith("192.168.11"):
            sys.stderr.write(
                f"UNKNOWN - Invalid start address format: {address}\n"
            )
            sys.exit(UNKNOWN)

        if address == "192.168.11.22":
            return 0, 0

        try:
            # Determine the opt value based on the starting byte of the IP address
            opt = 0
            if address.startswith("192.168.11.10"):
                opt = 1
            elif address.startswith("192.168.11.12"):
                opt = 2
            elif address.startswith("192.168.11.14"):
                opt = 3
            elif address.startswith("192.168.11.16"):
                opt = 4

            # Extract the dru number from the last byte of the IP address
            dru = int(address.strip()[-1:]) + 1

            return opt, dru
        except (IndexError, KeyError, ValueError):
            sys.stderr.write(f"UNKNOWN - Invalid address format: {address}\n")
            sys.exit(UNKNOWN)

    def _exit_message(self, code: int, message: str) -> None:
        """Prints an exit message with the specified code and message."""
        if code == CRITICAL:
            sys.stderr.write(f"CRITICAL - {message}\n")
        elif code == WARNING:
            sys.stderr.write(f"WARNING - {message}\n")
        else:
            sys.stderr.write(f"UNKNOWN - {message}\n")

    def transmit_and_receive(self) -> Tuple[int, str]:
        """
        Transmit commands and receive responses based on device and connection type.
        """
        try:
            device = self.parameters.get("device")
            address = self.parameters.get("address")
            baud_rate = self.parameters.get("baud_rate")

            os_name = os.name.lower()
            port_dmu, port_dru = self._get_ports(os_name)

            if device in [
                "dmu_serial_host",
                "dmu_serial_service",
                "dru_serial_host",
                "discovery_serial",
                "discovery_redboard_serial",
            ]:
                result = CommandTransmission._transmit_serial(
                    self.commands, port_dmu, baud_rate
                )
                if isinstance(result, int) and not result:
                    return CRITICAL, self._print_error(port_dmu)
                self.parameters.update(result)

            elif device == "dru_serial_service":
                result = CommandTransmission._transmit_serial(
                    self.commands, port_dru, baud_rate, timeout=10
                )
                if isinstance(result, int) and not result:
                    return CRITICAL, self._print_error(port_dru)
                self.parameters.update(result)
            else:
                result = CommandTransmission._transmit_tcp(
                    self.commands, address
                )
                if isinstance(result, int) and not result:
                    return CRITICAL, self._print_error(address)
                self.parameters.update(result)

            decoded_commands = self.extract_and_decode_received()
            if decoded_commands > 0:
                return OK, f"Received data from {device}"
            else:
                return (
                    WARNING,
                    f"No data received from {device}. Commands may not be supported.",
                )

        except Exception as e:
            return CRITICAL, f"Error: {e}"

    def _get_ports(self, os_name: str) -> Tuple[str, str]:
        """Get serial port names based on OS."""
        if os_name == "posix":
            return "/dev/ttyS0", "/dev/ttyS1"
        elif os_name == "nt":
            return "COM2", "COM3"
        else:
            sys.stderr.write("OS not recognized, using default action.\n")
            return "", ""

    def _print_error(self, device: str) -> str:
        """Print error message."""
        return f"No response from {device}"

    def extract_and_decode_received(self) -> int:
        """Extracts and decodes the received commands."""
        decoded_commands = 0
        for communication_protocol in self.commands:
            value = communication_protocol.get_reply_value()
            if value:
                decoded_commands += 1
                self.parameters.update(value)
        return decoded_commands