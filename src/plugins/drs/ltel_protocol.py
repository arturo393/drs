from src.plugins.drs.comunication_protocol import ComunicationProtocol


class LtelProtocol(ComunicationProtocol):
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


