from typing import Any

from src.plugins.drs.LtelProtocolBase import LTELProtocolBase



class LtelProtocol(LTELProtocolBase):
    """Communication protocol for individual LTEL commands."""

    def __init__(self, dru_id: int, command_name: Any, message_type: int):
        """Initialize LtelProtocol object."""
        super().__init__(dru_id)
        self.command_name = command_name
        self.message_type = message_type

    def generate_frame(self) -> str:
        """Generate a frame for the LTEL command."""
        length, code = self.command_name.value
        length_code = f"{length:02X}{code:04X}"
        data = length_code.ljust(length * 2, "0")

        command_unit = (
            f"{self._generate_common_header()}"
            f"{LTELProtocolBase.TX_RX:02X}"
            f"{LTELProtocolBase.UNKNOWN3:02X}"
            f"{self.message_type:02X}"
            f"{LTELProtocolBase.TX_RX2:02X}"
            f"{data}"
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
        return 17

    def _get_end_adjustment(self) -> int:
        """Return the adjustment to be made at the end of the reply."""
        return 5

    def _get_command_body_length(self) -> int:
        """Return the length of the command body."""
        return self._reply[14] - 3 if self._reply else 0