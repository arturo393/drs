from abc import abstractmethod

from crccheck.crc import Crc16Xmodem

from src.plugins.drs.decoder import Decoder
from src.plugins.drs.definitions.santone_commands import DataType, ResponseFlag

DONWLINK_MODULE = 0 << 7
UPLINK_MODULE = 1 << 7


class ComunicationProtocol:
    def __init__(self):
        self._reply_command_data = None
        self._reply = None
        self._reply_bytes = None
        self._command_type = None
        self._data = None
        self._dru_id = None
        self._length = None
        self._code = None
        self._data = None
        self._module_address = None
        self._module_link = None
        self._module_function = None
        self._command_number = None
        self._command_data = None
        self._response_flag = None
        self._command_body_length = None
        self._query = None
        self._query_bytes = None
        self._message = None
        self._decoder = Decoder()
        self._message_type = None

    @abstractmethod
    def generate_frame(self):
        """
        Abstract method to generate a frame.
        This method should be implemented by all subclasses.
        """
        pass

    @abstractmethod
    def is_valid_reply(self, reply):
        """
        Abstract method to generate a frame.
        This method should be implemented by all subclasses.
        """
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

    def set_reply_message(self, reply: bytearray):
        self._reply = reply

    def has_reply(self) -> bool:
        """
        Returns True if a reply has been set and its length is greater than 0,
        False otherwise.
        """
        return self._reply is not None and len(self._reply) > 0

    def save_if_valid(self, reply: bytearray) -> bool:
        if self.is_valid_reply(reply):
            self.set_reply_message(reply)
            return True
        return False
























