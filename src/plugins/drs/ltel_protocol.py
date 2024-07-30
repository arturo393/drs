from src.plugins.drs.comunication_protocol import CommunicationProtocol


class LtelProtocol(CommunicationProtocol):

    def __init___(self, dru_id, command_name, message_type):
        super().__init__()
        self.dru_id = dru_id
        self.command_name = command_name
        self.message_type = message_type

    def generate_frame(self):
        start_flag = "7E"
        unknown1 = 0x0101
        site_number = 0
        unknown2 = 0x0100
        unknown3 = 0x01
        tx_rx = 0x80
        tx_rx2 = 0xFF
        length = self.command_name.value[0]
        code = self.command_name.value[1]
        length_code = f"{length:02X}{code:04X}"
        data = length_code.ljust(length * 2, '0')
        cmd_unit = (
            f"{unknown1:04X}"
            f"{site_number:08X}"
            f"{self.dru_id}"
            f"{unknown2:04X}"
            f"{tx_rx:02X}"
            f"{unknown3:02X}"
            f"{self.message_type:02X}"
            f"{tx_rx2:02X}"
            f"{data}"
        )

        crc = self.generate_checksum(cmd_unit)
        return f"{start_flag}{cmd_unit}{crc}{start_flag}{start_flag}"

    def _is_valid_reply(self, reply: bytearray) -> bool:
        # Define necessary indices
        respond_flag_index = 10

        if not reply:
            return False

        self._response_flag = reply[respond_flag_index]
        if self._response_flag == ResponseFlag.SUCCESS:
            return True
        else:
            return False

    def _get_cmd_data_index(self) -> int:
        return 17

    def _get_end_adjustment(self) -> int:
        return 5  # Assuming 2 bytes for CRC and 3 bytes for end flags

    def _get_command_body_length(self) -> int:
        return self._reply[14] - 3 if self._reply else 0