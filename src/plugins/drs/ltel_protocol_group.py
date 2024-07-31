from typing import Any

from src.plugins.drs.LtelProtocolBase import LTELProtocolBase
from src.plugins.drs.definitions.santone_commands import ResponseFlag


class LTELProtocolGroup(LTELProtocolBase):
    """Communication protocol for LTEL command groups."""

    TX_RX = 0x80
    UNKNOWN3 = 0x01
    MESSAGE_TYPE = 0x02
    TX_RX2 = 0xFF

    def __init__(self, dru_id: int, cmd_name_group: Any):
        """Initialize LTELProtocolGroup object."""
        super().__init__(dru_id)
        self.cmd_name_group = cmd_name_group

    def generate_frame(self) -> str:
        """Generate a frame for the LTEL command group."""
        command_unit = (
            f"{self._generate_common_header()}"
            f"{self.TX_RX:02X}"
            f"{self.UNKNOWN3:02X}"
            f"{self.MESSAGE_TYPE:02X}"
            f"{self.TX_RX2:02X}"
            f"{self.cmd_name_group.value}"
        )
        return self._generate_ltel_frame(command_unit)

    def _is_valid_reply(self, reply: bytearray) -> bool:
        """Check if the reply is valid."""
        if not reply:
            return False

        respond_flag_index = 10
        self._response_flag = reply[respond_flag_index]
        return self._response_flag == ResponseFlag.SUCCESS

    def _get_cmd_data_index(self) -> int:
        """Return the starting index of the command body in the reply."""
        return 14

    def _get_end_adjustment(self) -> int:
        """Return the adjustment to be made at the end of the reply."""
        return 4

    def _get_command_body_length(self) -> int:
        """Return the length of the command body."""
        return len(self._reply) - self._get_cmd_data_index() - self._get_end_adjustment()