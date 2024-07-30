from abc import ABC, abstractmethod
from typing import Optional, Any
from crccheck.crc import Crc16Xmodem
from src.plugins.drs.decoder import Decoder
from src.plugins.drs.definitions.santone_commands import ResponseFlag


class CommunicationProtocol(ABC):
    DOWNLINK_MODULE = 0 << 7
    UPLINK_MODULE = 1 << 7

    def __init__(self):
        self._reply: Optional[bytearray] = None
        self._command_number: Optional[int] = None
        self._command_body_length: Optional[int] = None
        self._command_body: Optional[bytearray] = None

    @abstractmethod
    def generate_frame(self) -> str:
        """Generate a frame for the command."""
        pass

    @abstractmethod
    def _is_valid_reply(self, reply: bytearray) -> bool:
        """Check if the reply is valid."""
        pass

    def get_reply_value(self) -> Optional[Any]:
        """Extract and decode the reply value."""
        if not self.has_reply():
            return None

        try:
            self._extract_data_from_reply()
            return self._decode()
        except Exception as e:
            print(f"Error processing reply: {str(e)}")
            return None

    def _decode(self) -> Any:
        """Decode the command body."""
        if not self._command_number or not self._command_body:
            raise ValueError("Command number or body not set")

        try:
            decode_method = getattr(Decoder, f"_decode_{self._command_number.name}")
            return decode_method(self._command_body)
        except AttributeError:
            print(f"Command number {self._command_number} is not supported.")
            return {}

    @abstractmethod
    def _extract_data_from_reply(self) -> None:
        """Extract data from the reply."""
        pass

    def __str__(self) -> str:
        if self.has_reply():
            reply = self.bytearray_to_hex(self._reply)
            message = self.get_reply_message()
        else:
            reply = "No reply"
            message = ""

        return f"{self.generate_frame()} - {reply} - {message}"

    def set_command(self, command_number: int, command_body_length: int) -> None:
        """Set the command number and body length."""
        self._command_number = command_number
        self._command_body_length = command_body_length

    def get_reply_message(self) -> str:
        """Get a human-readable message for the reply."""
        if not self.has_reply() or len(self._reply) < 6:
            return "No message returned"

        response_flag = self._reply[5]
        messages = {
            ResponseFlag.SUCCESS: "Success",
            ResponseFlag.WRONG_COMMAND_NUMBER: "Wrong command",
            ResponseFlag.COMMAND_DATA_ERROR: "Command data error",
            ResponseFlag.COMMAND_BODY_LENGTH_ERROR: "Command body length error",
            ResponseFlag.OPERATION_FAILED: "Operation failed",
        }
        return messages.get(response_flag, f"Unknown message ({response_flag})")

    @staticmethod
    def generate_checksum(cmd: str) -> str:
        """Generate a checksum for the given command."""
        try:
            data = bytearray.fromhex(cmd)
        except ValueError:
            return ""

        crc = Crc16Xmodem.calc(data)
        crc = f"{crc:04X}"
        checksum = crc[2:4] + crc[0:2]
        checksum = checksum.upper()
        return checksum.replace('5E', '5E5D').replace('7E', '5E7D')

    @staticmethod
    def bytearray_to_hex(byte_array: bytearray) -> str:
        """Convert a bytearray to a hexadecimal string."""
        return ''.join(f"{byte:02X}" for byte in byte_array)

    def get_command_query_as_str(self) -> str:
        """Get the command query as a string."""
        return self.generate_frame()

    def get_command_query_as_bytearray(self) -> bytearray:
        """Get the command query as a bytearray."""
        return bytearray.fromhex(self.generate_frame())

    def _set_reply_message(self, reply: bytearray) -> None:
        """Set the reply message."""
        self._reply = reply

    def has_reply(self) -> bool:
        """Check if a reply has been set."""
        return self._reply is not None and len(self._reply) > 0

    def save_if_valid(self, reply: bytearray) -> bool:
        """Save the reply if it's valid."""
        if self._is_valid_reply(reply):
            self._set_reply_message(reply)
            return True
        return False
