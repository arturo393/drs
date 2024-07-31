from src.plugins.drs.comunication_protocol.decoder.decoder import Decoder


class LtelDecoder(Decoder):

    @staticmethod
    def _frequency_decode(command_body: bytes) -> float:
        """
        Decodes the frequency value from the command body.

        Args:
            command_body: The bytearray containing the command data.

        Returns:
            The decoded frequency value in MHz.
        """

        try:
            # Extract and convert the frequency value to an integer
            little = int.from_bytes(command_body, byteorder='little')
        except (TypeError, ValueError):
            # Handle invalid data format
            raise ValueError(f"Invalid command body: {command_body}")

        # Calculate the frequency in MHz
        frequency = little / 10000

        return frequency

    @staticmethod
    def _decode_frequencies(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) == 0:
            return {}
        frequencies = {}
        frequencies.update(
            LtelDecoder._decode_uplink_start_frequency(command_body[3 + 0:7]))
        # frequencies.update(LtelDecoder._decode_downlink_start_frequency(command_body[3 + 0:3 + 4]))
        frequencies.update(
            LtelDecoder._decode_work_bandwidth(command_body[3 + 7:14]))
        frequencies.update(
            LtelDecoder._decode_channel_bandwidth(command_body[3 + 14:28]))
        return frequencies

    @staticmethod
    def _decode_channel(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) != 85:
            return {}
        channel_info = {}
        channel_info.update(
            LtelDecoder._decode_channel_switch_bit(command_body[3:5]))
        channel_info.update(
            LtelDecoder._decode_channel_1_number(command_body[3 + 5:10]))
        channel_info.update(
            LtelDecoder._decode_channel_2_number(command_body[3 + 10:15]))
        channel_info.update(
            LtelDecoder._decode_channel_3_number(command_body[3 + 15:20]))
        channel_info.update(
            LtelDecoder._decode_channel_4_number(command_body[3 + 20:25]))
        channel_info.update(
            LtelDecoder._decode_channel_5_number(command_body[3 + 25:30]))
        channel_info.update(
            LtelDecoder._decode_channel_6_number(command_body[3 + 30:35]))
        channel_info.update(
            LtelDecoder._decode_channel_7_number(command_body[3 + 35:40]))
        channel_info.update(
            LtelDecoder._decode_channel_8_number(command_body[3 + 40:45]))
        channel_info.update(
            LtelDecoder._decode_channel_9_number(command_body[3 + 45:50]))
        channel_info.update(
            LtelDecoder._decode_channel_10_number(command_body[3 + 50:55]))
        channel_info.update(
            LtelDecoder._decode_channel_11_number(command_body[3 + 55:60]))
        channel_info.update(
            LtelDecoder._decode_channel_12_number(command_body[3 + 60:65]))
        channel_info.update(
            LtelDecoder._decode_channel_13_number(command_body[3 + 65:70]))
        channel_info.update(
            LtelDecoder._decode_channel_14_number(command_body[3 + 70:75]))
        channel_info.update(
            LtelDecoder._decode_channel_15_number(command_body[3 + 75:80]))
        channel_info.update(
            LtelDecoder._decode_channel_16_number(command_body[3 + 80:85]))
        return channel_info

    @staticmethod
    def _decode_parameters(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 20:
            return {}
        parameters = {}
        parameters.update(LtelDecoder._decode_uplink_att(command_body[3 + 0:4]))
        parameters.update(LtelDecoder._decode_downlink_att(command_body[3 + 4:8]))
        parameters.update(LtelDecoder._decode_working_mode(command_body[3 + 8:12]))
        parameters.update(LtelDecoder._decode_downlink_vswr(
            command_body[3 + 12:16]))
        parameters.update(LtelDecoder._decode_downlink_output_power(
            command_body[3 + 16:20]))
        parameters.update(LtelDecoder._decode_uplink_input_power(
            command_body[3 + 20:24]))
        parameters.update(LtelDecoder._decode_power_amplifier_temperature(
            command_body[3 + 24:28]))

        return parameters

    @staticmethod
    def _decode_uplink_att(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) != 1:
            return {}
        return {
            "upAtt": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_downlink_att(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) != 1:
            return {}
        return {
            "dlAtt": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_switch_bit(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        channels = {}
        for i in range(15, -1, -1):
            bit = (command_body[0] >> i) & 1
            status = "ON" if bit == 0 else "OFF"
            channel_number = 1 + i
            channels[f"channel_{channel_number}_status"] = status
            i = i + 1
        return channels

    @staticmethod
    def _decode_working_mode(command_body):
        """Decodes the broadband switching command."""
        if len(command_body) == 0:
            return {}
        working_mode = {
            3: "Channel Mode",
            2: "WideBand Mode",
        }
        return {"working_mode": working_mode.get(command_body[0], "Unknown Mode")}

    @staticmethod
    def _decode_uplink_start_frequency(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 4:
            return {}
        return {
            "uplink_start_frequency": LtelDecoder._frequency_decode(command_body),
        }

    @staticmethod
    def _decode_downlink_start_frequency(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 4:
            return {}
        return {
            "downlink_start_frequency": LtelDecoder._frequency_decode(command_body),
        }

    @staticmethod
    def _decode_work_bandwidth(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 4:
            return {}
        return {
            "work_bandwidth": LtelDecoder._frequency_decode(command_body),
        }

    @staticmethod
    def _decode_channel_bandwidth(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 4:
            return {}
        return {
            "channel_bandwidth": LtelDecoder._frequency_decode(command_body),
        }

    @staticmethod
    def _decode_channel_1_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_1_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_2_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_2_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_3_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_3_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_4_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_4_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_5_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_5_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_6_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_6_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_7_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_7_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_8_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_8_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_9_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_9_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_10_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_10_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_11_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_11_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_12_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_12_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_13_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_13_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_14_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_14_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_15_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_15_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_channel_16_number(command_body):
        """Decodes channel number"""
        if len(command_body) != 2:
            return {}
        return {
            "channel_16_number": int.from_bytes(command_body, byteorder='little'),
        }

    @staticmethod
    def _decode_downlink_vswr(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) != 1:
            return {}
        little = int.from_bytes(command_body, byteorder='little')
        vswr = little / 10
        return {
            "downlink_vswr": vswr,
        }

    @staticmethod
    def _decode_power_amplifier_temperature(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) != 1:
            return {}
        little = int.from_bytes(command_body, byteorder='little')
        power_amlpifier_temperature = little
        return {
            "power_amplifier_temperature": power_amlpifier_temperature,
        }

    @staticmethod
    def _decode_downlink_output_power(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) != 1:
            return {}
        little = int.from_bytes(command_body, byteorder='little')
        downlink_output_power = little
        return {
            "downlink_output_power": downlink_output_power,
        }

    @staticmethod
    def _decode_uplink_input_power(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        little = int.from_bytes(command_body, byteorder='little')
        uplink_input_power = little
        return {
            "uplink_input_power": uplink_input_power,
        }
