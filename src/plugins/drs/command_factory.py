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
            device: str, parameters: Dict[str, Any]
    ) -> List[CommunicationProtocol]:
        """Creates a list of group query commands based on the device type."""
        commands = []
        cmd_group = CommandFactory.COMMAND_CLASS_MAP.get(device)

        if not cmd_group:
            return commands  # Return an empty list if device is not found

        opt = parameters["optical_port"]
        dru = parameters["device_number"]
        dru_id = f"{opt}{dru}"

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
