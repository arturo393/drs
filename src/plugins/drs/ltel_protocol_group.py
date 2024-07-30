from src.plugins.check_status import ResponseFlag
from src.plugins.drs.comunication_protocol import CommunicationProtocol


class LTELProtocolGroup(CommunicationProtocol):


    def __init__(self, dru_id, cmd_name_group):
        super().__init__()
        self.dru_id = dru_id
        self.cmd_name_group = cmd_name_group

    def generate_frame(self):
        # This method now implements the abstract method from the parent class
        start_flag = "7E"
        unknown1 = 0x0101
        site_number = 0
        unknown2 = 0x0100
        tx_rx = 0x80
        unknown3 = 0x01
        message_type = 0x02
        tx_rx2 = 0xFF
        data_group = self.cmd_name_group.value
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
        crc = self.generate_checksum(cmd_unit)
        return f"{start_flag}{cmd_unit}{crc}{start_flag}{start_flag}"

    def _is_valid_reply(self, reply: bytearray) -> bool:

        if not reply:
            return False

        respond_flag_index = 10

        self._response_flag = reply[respond_flag_index]
        if self._response_flag == ResponseFlag.SUCCESS:
            return True
        else:
            return False

    def _get_cmd_data_index(self) -> int:
        return 14

    def _get_end_adjustment(self) -> int:
        return 4

    def _get_command_body_length(self) -> int:
        return len(self._reply) - self._get_cmd_data_index() - self._get_end_adjustment()