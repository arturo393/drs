from src.plugins.check_status import ResponseFlag
from src.plugins.drs.comunication_protocol import CommunicationProtocol
from src.plugins.drs.definitions.santone_commands import DataType


class SantoneProtocol(CommunicationProtocol):
    """Communication protocol for Santone devices."""

    START_FLAG = "7E"
    MODULE_FUNCTION = 0x07

    def __init__(
        self,
        command_number: int,
        command_body_length: int,
        command_data: int,
        module_address: int = 0,
    ):
        """Initialize SantoneProtocol object."""
        super().__init__()
        self._command_number = command_number
        self._command_data = command_data
        self._command_body_length = command_body_length
        self._module_address = module_address

    def generate_frame(self) -> str:
        """Generate a frame for the Santone command."""
        command_data = f"{self._command_data:02X}" if self._command_data >= 0 else ""
        command_unit = (
            f"{self.MODULE_FUNCTION:02X}"
            f"{self._module_address:02X}"
            f"{DataType.DATA_INITIATION.value:02X}"
            f"{self._command_number:02X}"
            f"{ResponseFlag.SUCCESS.value:02X}"
            f"{self._command_body_length:02X}"
            f"{command_data}"
        )
        crc = self.generate_checksum(command_unit)
        return f"{self.START_FLAG}{command_unit}{crc}{self.START_FLAG}"

    def _is_valid_reply(self, reply: bytearray) -> bool:
        """Check if the reply is valid."""
        if len(reply) < 7:
            return False

        cmd_number_index = 4
        respond_flag_index = 5

        if (
            reply[cmd_number_index] != self._command_number
            or reply[respond_flag_index] != ResponseFlag.SUCCESS.value
        ):
            return False

        return True

    def _get_cmd_data_index(self) -> int:
        """Return the starting index of the command body in the reply."""
        return 7

    def _get_end_adjustment(self) -> int:
        """Return the adjustment to be made at the end of the reply."""
        return 3

    def _get_command_body_length(self) -> int:
        """Return the length of the command body."""
        return self._reply[6] if self._reply else 0