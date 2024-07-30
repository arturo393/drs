from src.plugins.drs.comunication_protocol import CommunicationProtocol


class LtelProtocol(CommunicationProtocol):
    def _is_valid_reply(self, reply: bytearray) -> bool:
        """
        Decodes a LtelDru command and handles the processing of command data.

        Args:
            command (ComunicationProtocol): The command to decode.

        Returns:
            int: The number of decoded commands.
        """
        try:
            # Check if command.reply is empty; return 0 if so
            if not reply:
                return False

            # Define necessary indices
            respond_flag_index = 10
            cmd_body_length_index = 14
            cmd_data_index = 17

            # Extract response flag, command body length, and command body
            # Catch IndexError if command.reply is shorter than expected
            try:
                self._response_flag = reply[respond_flag_index]
                self._command_body_length = reply[cmd_body_length_index] - 3
                self._command_body = reply[cmd_data_index:
                                                   cmd_data_index + command_body_length]
            except IndexError as e:
                return False

            # Check if response flag indicates success
            if response_flag == ResponseFlag.SUCCESS:
                command.reply_command_data = command_body
                # Attempt to decode command number
                try:
                    command.message = Decoder.ltel_decode(command_body)
                except (TypeError, ValueError) as e:
                    sys.stderr.write(
                        f"UNKNOWN - Cannot decode command number: {e}")
                    sys.exit(UNKNOWN)
                return 1
            else:
                return 0

        except Exception as e:
            sys.stderr.write(
                f"UNKNOWN - An error occurred during command decoding: {e}")
            sys.exit(UNKNOWN)


    def _extract_data_from_reply(self) -> None:
        pass

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


