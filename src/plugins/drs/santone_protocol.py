from src.plugins.check_status import ResponseFlag
from src.plugins.drs.comunication_protocol import CommunicationProtocol
from src.plugins.drs.decoder import Decoder
from src.plugins.drs.definitions.santone_commands import DataType


class SantoneProtocol(CommunicationProtocol):

    def __init__(self, command_number, command_body_length, command_data):
        super().__init__()
        self._command_number = command_number
        self._command_data = command_data
        self._command_body_length = command_body_length
        self._DOWNLINK_MODULE = 0 << 7
        self._UPLINK_MODULE = 1 << 7

    def generate_frame(self):
        start_flag = "7E"
        module_address = self._DOWNLINK_MODULE | 0
        module_function = 0x07
        command_type = DataType.DATA_INITIATION
        response_flag = ResponseFlag.SUCCESS
        command_data = f"{self._command_data:02X}" if self._command_data >= 0 else ""
        cmd_unit = (
            f"{module_function:02X}"
            f"{module_address:02X}"
            f"{command_type:02X}"
            f"{self._command_number:02X}"
            f"{response_flag:02X}"
            f"{self._command_body_length:02X}"
            f"{command_data}"
        )

        crc = self.generate_checksum(cmd_unit)
        return f"{start_flag}{cmd_unit}{crc}{start_flag}"

    def _is_valid_reply(self, reply) -> bool:
        """
        Checks if the reply is valid for an IFBoard command.
        Returns True if the reply is valid, False otherwise.
        """
        # Minimum length check
        if len(reply) < 7:  # Minimum length to include all necessary fields
            return False

        cmd_number_index = 4
        respond_flag_index = 5

        # Check if command number matches
        if reply[cmd_number_index] != self._command_number.value:
            return False

        # Check if response flag indicates success
        if reply[respond_flag_index] != ResponseFlag.SUCCESS:
            return False

        # Additional checks cans be added here if needed
        # For example, checking module_function or data_type if they should have specific values

        return True

    def _get_cmd_data_index(self) -> int:
        return 7

    def _get_end_adjustment(self) -> int:
        return 3  # Assuming 2 bytes for CRC and 1 byte for end flag

    def _get_command_body_length(self) -> int:
        return self._reply[6] if self._reply else 0