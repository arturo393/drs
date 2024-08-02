from typing import Any

from .ltel_protocol_base import LTELProtocolBase


class LtelProtocol(LTELProtocolBase):
    """Communication protocol for individual LTEL commands."""

    CMD_DATA_INDEX = 17
    END_ADJUSTMENT = 5
    BODY_LENGTH_INDEX = 14
    BODY_LENGTH_ADJUSTMENT = 3

    def __init__(self, dru_id: str, command_name: Any, message_type: int):
        """Initialize LtelProtocol object."""
        super().__init__(dru_id)
        self.command_name = command_name
        self.message_type = message_type

    def generate_frame(self) -> str:
        """Generate a frame for the LTEL command."""
        length, code = self.command_name.value
        length_code = f"{length:02X}{code:04X}"
        data = length_code.ljust(length * 2, "0")

        command_unit = f"{self._generate_common_header()}{data}"
        return self._generate_ltel_frame(command_unit)

    def _get_cmd_data_index(self) -> int:
        """Return the starting index of the command body in the reply."""
        return self.CMD_DATA_INDEX

    def _get_end_adjustment(self) -> int:
        """Return the adjustment to be made at the end of the reply."""
        return self.END_ADJUSTMENT

    def _get_command_body_length(self) -> int:
        """Return the length of the command body."""
        return (
            self._reply[self.BODY_LENGTH_INDEX] - self.BODY_LENGTH_ADJUSTMENT
            if self._reply
            else 0
        )

