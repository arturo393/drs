from typing import Any

from src.plugins.drs.comunication_protocol.ltel.ltel_protocol_base import LTELProtocolBase


class LTELProtocolGroup(LTELProtocolBase):
    """Communication protocol for LTEL command groups."""

    CMD_DATA_INDEX = 14
    END_ADJUSTMENT = 4

    def __init__(self, dru_id: str, cmd_name_group: Any):
        """Initialize LTELProtocolGroup object."""
        super().__init__(dru_id)
        self.cmd_name_group = cmd_name_group

    def generate_frame(self) -> str:
        """Generate a frame for the LTEL command group."""
        command_unit = f"{self._generate_common_header()}{self.cmd_name_group.value}"
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
            len(self._reply) - self._get_cmd_data_index() - self._get_end_adjustment()
        )