from abc import abstractmethod

from crccheck.crc import Crc16Xmodem

from src.plugins.drs.decoder import Decoder
from src.plugins.drs.definitions.santone_commands import DataType, ResponseFlag

DONWLINK_MODULE = 0 << 7
UPLINK_MODULE = 1 << 7


class ComunicationProtocol:
    def __init__(self):
        pass

    @abstractmethod
    def generate_frame(self):
        """
        Abstract method to generate a frame.
        This method should be implemented by all subclasses.
        """
        pass

    @abstractmethod
    def _is_valid_reply(self, reply):
        """
        Abstract method to generate a frame.
        This method should be implemented by all subclasses.
        """
        pass

    @abstractmethod
    def get_reply_value(self):
        if self.has_reply():
            self._extract_data_from_reply()
            decoded_reply = self._decode()
        else:
            decoded_reply = None

        return decoded_reply

    @abstractmethod
    def _decode(self):
        """Decodes a command number."""
        try:
            return getattr(Decoder, f"_decode_{self._command_number.name}")(self._command_body)
        except AttributeError:
            print(f" Command number {self._command_number} is not supported.")
            return {}

    @abstractmethod
    def _extract_data_from_reply(self):
        pass

    def __str__(self):
        if self.reply:
            reply = self.bytearray_to_hex(self.reply)
            message = self.get_reply_message()
        else:
            reply = "No reply"
            message = ""

        return f"{self.query} -  {reply} - {message}"

    def set_command(self, command_number, command_body_length):
        self.command_number = command_number
        self.command_body_length = command_body_length

    def get_reply_message(self):
        if len(self.reply) >= 6:
            response_flag = self.reply[5]
            # ... your other code ...
        else:
            return f"No message return "

        messages = {
            ResponseFlag.SUCCESS: "Success",
            ResponseFlag.WRONG_COMMAND_NUMBER: "Wrong command",
            ResponseFlag.COMMAND_DATA_ERROR: "Command data error",
            ResponseFlag.COMMAND_BODY_LENGTH_ERROR: "Command body length error",
            ResponseFlag.OPERATION_FAILED: "Operation failed",
        }
        return messages.get(response_flag, f"Unknown message ({response_flag})")

    @staticmethod
    def generate_checksum(cmd):
        try:
            data = bytearray.fromhex(cmd)
        except ValueError:
            return ""

        crc = Crc16Xmodem.calc(data)
        crc = f"0x{crc:04X}"

        if len(crc) == 5:
            checksum = crc[3:5] + '0' + crc[2:3]
        else:
            checksum = crc[4:6] + crc[2:4]

        checksum = checksum.upper()
        checksum_new = checksum.replace('5E', '5E5D').replace('7E', '5E7D')

        return checksum_new

    @staticmethod
    def bytearray_to_hex(byte_array):
        return ''.join(format(byte, '02X') for byte in byte_array)

    def get_command_query_as_str(self):
        return self.generate_frame()

    def get_command_query_as_bytearray(self):
        return bytearray.fromhex(self.generate_frame())

    def _set_reply_message(self, reply: bytearray):
        self._reply = reply

    def has_reply(self) -> bool:
        """
        Returns True if a reply has been set and its length is greater than 0,
        False otherwise.
        """
        return self._reply is not None and len(self._reply) > 0

    def save_if_valid(self, reply: bytearray) -> bool:
        if self._is_valid_reply(reply):
            self._set_reply_message(reply)
            return True
        return False
























