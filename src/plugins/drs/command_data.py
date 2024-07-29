from crccheck.crc import Crc16Xmodem

from src.plugins.drs.decoder import Decoder
from src.plugins.drs.definitions.santone_commands import DataType, ResponseFlag

DONWLINK_MODULE = 0 << 7
UPLINK_MODULE = 1 << 7


class CommandData:

    def __init__(self):
        self.reply_command_data = None
        self.reply = None
        self.reply_bytes = None
        self.command_type = None
        self.data = None
        self.dru_id = None
        self.length = None
        self.code = None
        self.data = None
        self.module_address = None
        self.module_link = None
        self.module_function = None
        self.command_number = None
        self.command_data = None
        self.response_flag = None
        self.command_body_length = None
        self.query = None
        self.query_bytes = None
        self.message = None
        self.decoder = Decoder()
        self.message_type = None

    def generate_ltel_comunication_board_frame(self, dru_id, cmd_name, message_type):
        start_flag = "7E"
        end_flag = "7F"
        unknown1 = 0x0101
        site_number = 0
        self.dru_id = dru_id
        unknown2 = 0x0100
        unknown3 = 0x01
        tx_rx = 0x80
        tx_rx2 = 0xFF
        length = cmd_name.value[0]
        code = cmd_name.value[1]
        length_code = f"{length:02X}{code:04X}"
        data = length_code.ljust(length * 2, '0')
        self.command_number = cmd_name
        cmd_unit = (
            f"{unknown1:04X}"
            f"{site_number:08X}"
            f"{self.dru_id}"
            f"{unknown2:04X}"
            f"{tx_rx:02X}"
            f"{unknown3:02X}"
            f"{message_type:02X}"
            f"{tx_rx2:02X}"
            f"{data}"
        )

        # 7E010100000000110100800102FF04030500ACA27E sw chino
        # 7E010100000000110100800102FF04030500ACA27E sw uqomm
        crc = self.generate_checksum(cmd_unit)
        self.query = f"{start_flag}{cmd_unit}{crc}{start_flag}{start_flag}"

    def generate_comm_board_group_frame(self, dru_id, cmd_name_group):
        start_flag = "7E"
        end_flag = "7F"
        unknown1 = 0x0101
        site_number = 0
        self.dru_id = dru_id
        unknown2 = 0x0100
        tx_rx = 0x80
        unknown3 = 0x01
        message_type = 0x02
        tx_rx2 = 0xFF
        data_group = cmd_name_group.value
        self.command_number = cmd_name_group
        cmd_unit = (
            f"{unknown1:04X}"
            f"{site_number:08X}"
            f"{self.dru_id}"
            f"{unknown2:04X}"
            f"{tx_rx:02X}"
            f"{unknown3:02X}"
            f"{message_type:02X}"
            f"{tx_rx2:02X}"
            f"{data_group}"
        )

        # 7E010100000000110100800102FF04030500ACA27E sw chino
        # 7E010100000000110100800102FF04030500ACA27E sw uqomm
        crc = self.generate_checksum(cmd_unit)
        self.query = f"{start_flag}{cmd_unit}{crc}{start_flag}{start_flag}"

    def generate_ifboard_frame(self, command_number, command_data, command_body_length):
        """Generates an IFBoard frame for the given command number, command data, and command body length.

        Args:
            command_number: The command number.
            command_data: The command data.
            command_body_length: The command body length.

        Returns:
            An IFBoard len frame.
        """

        start_flag = "7E"
        end_flag = "7F"
        self.command_number = command_number
        self.command_body_length = command_body_length
        self.command_data = command_data
        module_address = DONWLINK_MODULE | 0
        module_function = 0x07
        command_type = DataType.DATA_INITIATION
        response_flag = ResponseFlag.SUCCESS
        cmd_unit = ""
        if isinstance(command_data, str):
            command_data = f"{command_data}"
        elif isinstance(command_data, int):
            if command_data < 0:
                command_data = ""
            else:
                command_data = f"{command_data:02X}"

        cmd_unit += f"{module_function:02X}"
        cmd_unit += f"{module_address:02X}"
        cmd_unit += f"{command_type:02X}"
        cmd_unit += f"{command_number:02X}"
        cmd_unit += f"{response_flag:02X}"
        cmd_unit += f"{command_body_length:02X}"
        cmd_unit += f"{command_data}"

        crc = self.generate_checksum(cmd_unit)
        self.query = f"{start_flag}{cmd_unit}{crc}{start_flag}"
        return len(self.query)

    def __str__(self):
        if self.reply:
            reply = self.bytearray_to_hex(self.reply)
            message = self.get_reply_message()

        else:
            reply = "No reply"
            message = ""
            decode = ""

        return f"{self.query} -  {reply} - {message}"

    def set_command(self, command_number, command_body_length):
        self.command_number = command_number
        self.command_body_length = command_body_length

    def get_reply_message(self):
        if len(self.reply) >= 6:
            response_flag = self.reply[5]
            # ... your other code ...
        else:
            # Handle the case when the reply is too short
            return f"No message return "

        messages = {
            ResponseFlag.SUCCESS: "Success",
            ResponseFlag.WRONG_COMMAND_NUMBER: "Wrong command",
            ResponseFlag.COMMAND_DATA_ERROR: "Command data error",
            ResponseFlag.COMMAND_BODY_LENGTH_ERROR: "Command body length error",
            ResponseFlag.OPERATION_FAILED: "Operation failed",
        }
        if response_flag in messages:
            return messages[response_flag]
        else:
            return f"Unknown message ({response_flag})"

    def generate_checksum(self, cmd):
        """
        -Description: this fuction calculate the checksum for a given comand
        -param text: string with the data, ex device = 03 , id = 03 cmd = 0503110000
        -return: cheksum for the given command
        """
        try:
            data = bytearray.fromhex(cmd)
        except ValueError as e:
            return ""

        crc = Crc16Xmodem.calc(data)
        crc = f"0x{crc:04X}"

        # print("crc: %s" % crc)

        if len(crc) == 5:
            checksum = crc[3:5] + '0' + crc[2:3]
        else:
            checksum = crc[4:6] + crc[2:4]

        checksum = checksum.upper()
        checksum_new = checksum.replace('5E', '5E5D')
        checksum_new = checksum.replace('7E', '5E7D')

        return checksum_new

    def bytearray_to_hex(self, byte_array):
        hex_string = ''.join(format(byte, '02X') for byte in byte_array)
        return hex_string
