from typing import Dict, Any, Type, List

from src.plugins.drs.comunication_protocol.comunication_protocol import (
    CommunicationProtocol,
)
from src.plugins.drs.comunication_protocol.ltel.ltel_protocol import LtelProtocol
from src.plugins.drs.comunication_protocol.ltel.ltel_protocol_group import (
    LTELProtocolGroup,
)
from src.plugins.drs.comunication_protocol.santone_protocol import SantoneProtocol
from src.plugins.drs.definitions.ltel_commands import (
    CommBoardGroupCmd,
    CommBoardCmd,
)
from src.plugins.drs.definitions.santone_commands import (
    DRSMasterCommand,
    DRSRemoteCommand,
    DiscoveryCommand,
    DiscoveryRedBoardCommand,
)


class CommandFactory:
    """Factory class for creating communication protocol commands."""

    COMMAND_CLASS_MAP = {
        "dmu_ethernet": DRSMasterCommand,
        "dru_ethernet": DRSRemoteCommand,
        "discovery_ethernet": DiscoveryCommand,
        "discovery_serial": DiscoveryCommand,
        "dmu_serial_service": DRSMasterCommand,
        "dru_serial_service": CommBoardGroupCmd,
        "discovery_redboard_serial": DiscoveryRedBoardCommand,
    }



    @staticmethod
    def create_group_query_commands(
            device: str, dru_id: str) -> List[CommunicationProtocol]:
        """Creates a list of group query commands based on the device type."""
        commands = []
        cmd_group = CommandFactory.COMMAND_CLASS_MAP.get(device)

        return CommandFactory._get_command_from_group(cmd_group, commands, dru_id)

    @staticmethod
    def create_single_command(self, dru_id: str, cmd_number):

        """Generates a single command frame.

        Returns:
            int: The length of the command frame, in bytes.
        """
        commands = []
        cmd_group = CommandFactory._get_command_value(cmd_number)
        return CommandFactory._get_command_from_group(cmd_group, commands, dru_id)

    @staticmethod
    def _get_command_from_group(cmd_group, commands, dru_id):
        if not cmd_group:
            return commands  # Return an empty list if device is not found
        if cmd_group == CommBoardCmd:
            commands.extend(
                [LtelProtocol(dru_id, cmd_name, 0x02) for cmd_name in cmd_group]
            )
        elif cmd_group == CommBoardGroupCmd:
            commands.extend(
                [LTELProtocolGroup(dru_id, cmd) for cmd in cmd_group]
            )
        else:
            commands.extend(
                [SantoneProtocol(cmd_name, 0x00, -1) for cmd_name in cmd_group]
            )
        return commands
    @staticmethod
    def _get_command_comm_board_value(cmd_name):
        int_number = cmd_name

        for command in CommBoardCmd:
            if command.value[1] == int_number:
                return command
        return None

    @staticmethod
    def _get_command_value(value: object) -> object:

        for _, cmd_group in CommandFactory.COMMAND_CLASS_MAP:
            try:
                # Attempt to create an instance of the command group with the value
                result = cmd_group(value)
                # If successful, return the result
                return result
            except ValueError:
                # If ValueError occurs, continue to the next command group
                continue

                # If no matching command group is found, return the original value
        return value
