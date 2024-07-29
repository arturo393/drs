import struct

class Decoder:

    def decode(command_number, command_body):
        """Decodes a command number."""
        try:
            return getattr(Decoder, f"_decode_{command_number.name}")(command_body)
        except AttributeError:
            print(f" Command number {command_number} is not supported.")
            return {}

    def ifboard_decode(self, command_number, command_body):
        """Decodes a command number."""
        try:
            return getattr(Decoder, f"_decode_{command_number.name}")(command_body)
        except AttributeError:
            print(f" Command number {command_number} is not supported.")
            return {}

    def ltel_decode(command_number, command_body):
        """Decodes a command number."""
        try:
            return getattr(Decoder, f"_decode_{command_number.name}")(command_body)
        except AttributeError:
            print(f" Command number {command_number} is not supported.")
            return {}

    def comm_board_decode(command_number, command_body):
        """Decodes a command number."""
        try:
            return getattr(Decoder, f"_decode_{command_number.name}")(command_body)
        except AttributeError:
            print(f" Command number {command_number} is not supported.")
            return {}

    @staticmethod
    def _decode_optical_module_hw_parameters(array):
        parameters = {}
        step = 4

        for i in range(0, 15, step):
            test = array[i:i + step]
            fb_number = i // step
            rx_pwr = array[i:i + 2]
            tx_pwr = array[i + 2:i + 4]
            rx_pwr = Decoder.optic_module_power_convert(rx_pwr, 0.001)
            tx_pwr = Decoder.optic_module_power_convert(tx_pwr, 0.001)
            parameter_name = "Fb{}_Rx_Pwr".format(
                fb_number,
            )
            parameters[parameter_name] = rx_pwr

            parameter_name = "Fb{}_Tx_Pwr".format(
                fb_number,
            )
            parameters[parameter_name] = tx_pwr

        for i in range(16, len(array), 2):
            if i == 16:
                fb_number = i % 16
            else:
                fb_number = (i % 16) - 1

            temp = array[i:i + 2]
            temp = Decoder.optic_module_power_convert(temp, 0.1)

            parameter_name = "Fb{}_Temp".format(
                fb_number,
            )
            parameters[parameter_name] = temp

        return parameters

    def calculate_tx_power(bytes_list):
        """Calculates the TX power of a fiber from a list of bytes.

        Args:
          bytes_list: A list of bytes containing the TX power data.

        Returns:
          The TX power of the fiber in dBm.
        """

        tx_power = struct.unpack(">H", bytes_list)[0]
        tx_power = tx_power * 0.1
        return tx_power

    def calculate_rx_power(bytes_list):
        """Calculates the RX power of a fiber from a list of bytes.

        Args:
          bytes_list: A list of bytes containing the RX power data.

        Returns:
          The RX power of the fiber in dBm.
        """

        rx_power = struct.unpack(">H", bytes_list)[0]
        rx_power = rx_power * 0.1
        return rx_power

    def calculate_temperature(bytes_list):
        """Calculates the temperature of a fiber from a list of bytes.

        Args:
          bytes_list: A list of bytes containing the temperature data.

        Returns:
          The temperature of the fiber in degrees Celsius.
        """

        temperature = struct.unpack(">H", bytes_list)[0]
        temperature = temperature * 0.001
        return temperature

    @staticmethod
    def _decode_frequencies(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) == 0:
            return {}
        frequencies = {}
        frequencies.update(Decoder._decode_uplink_start_frequency(command_body[3 + 0:7]))
        # frequencies.update(Decoder._decode_downlink_start_frequency(command_body[3 + 0:3 + 4]))
        frequencies.update(Decoder._decode_work_bandwidth(command_body[3 + 7:14]))
        frequencies.update(Decoder._decode_channel_bandwidth(command_body[3 + 14:28]))
        return frequencies

    @staticmethod
    def _decode_channel(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) != 85:
            return {}
        channel_info = {}
        channel_info.update(Decoder._decode_channel_switch_bit(command_body[3:5]))
        channel_info.update(Decoder._decode_channel_1_number(command_body[3 + 5:10]))
        channel_info.update(Decoder._decode_channel_2_number(command_body[3 + 10:15]))
        channel_info.update(Decoder._decode_channel_3_number(command_body[3 + 15:20]))
        channel_info.update(Decoder._decode_channel_4_number(command_body[3 + 20:25]))
        channel_info.update(Decoder._decode_channel_5_number(command_body[3 + 25:30]))
        channel_info.update(Decoder._decode_channel_6_number(command_body[3 + 30:35]))
        channel_info.update(Decoder._decode_channel_7_number(command_body[3 + 35:40]))
        channel_info.update(Decoder._decode_channel_8_number(command_body[3 + 40:45]))
        channel_info.update(Decoder._decode_channel_9_number(command_body[3 + 45:50]))
        channel_info.update(Decoder._decode_channel_10_number(command_body[3 + 50:55]))
        channel_info.update(Decoder._decode_channel_11_number(command_body[3 + 55:60]))
        channel_info.update(Decoder._decode_channel_12_number(command_body[3 + 60:65]))
        channel_info.update(Decoder._decode_channel_13_number(command_body[3 + 65:70]))
        channel_info.update(Decoder._decode_channel_14_number(command_body[3 + 70:75]))
        channel_info.update(Decoder._decode_channel_15_number(command_body[3 + 75:80]))
        channel_info.update(Decoder._decode_channel_16_number(command_body[3 + 80:85]))
        return channel_info

    @staticmethod
    def _decode_parameters(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 20:
            return {}
        parameters = {}
        parameters.update(Decoder._decode_uplink_att(command_body[3 + 0:4]))
        parameters.update(Decoder._decode_downlink_att(command_body[3 + 4:8]))
        parameters.update(Decoder._decode_working_mode(command_body[3 + 8:12]))
        parameters.update(Decoder._decode_downlink_vswr(command_body[3 + 12:16]))
        parameters.update(Decoder._decode_downlink_output_power(command_body[3 + 16:20]))
        parameters.update(Decoder._decode_uplink_input_power(command_body[3 + 20:24]))
        parameters.update(Decoder._decode_power_amplifier_temperature(command_body[3 + 24:28]))

        return parameters

    @staticmethod
    def _s8(byte):
        if byte > 127:
            return (256 - byte) * (-1)
        else:
            return byte

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
            "uplink_start_frequency": Decoder._frequency_decode(command_body),
        }

    @staticmethod
    def _decode_downlink_start_frequency(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 4:
            return {}
        return {
            "downlink_start_frequency": Decoder._frequency_decode(command_body),
        }

    @staticmethod
    def _decode_work_bandwidth(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 4:
            return {}
        return {
            "work_bandwidth": Decoder._frequency_decode(command_body),
        }

    @staticmethod
    def _decode_channel_bandwidth(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 4:
            return {}
        return {
            "channel_bandwidth": Decoder._frequency_decode(command_body),
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

    @staticmethod
    def _decode_rx0_broadband_power(command_body):
        """Decodes the broadband power query command."""
        if len(command_body) < 2:
            return {}

        rx0_broadband_power = Decoder.power_convert(command_body)

        return {
            "rx0_broadband_power": rx0_broadband_power,
        }

    @staticmethod
    def _decode_rx1_broadband_power(command_body):
        """Decodes the broadband power query command."""
        if len(command_body) < 2:
            return {}

        rx1_broadband_power = Decoder.power_convert(command_body)

        return {
            "rx1_broadband_power": rx1_broadband_power,
        }

    @staticmethod
    def _decode_subband_bandwidth(command_body):
        if len(command_body) < 6:
            return {}
        else:
            ch = 1
            subband_bandwidth = {}
            for i in range(0, 32, 2):
                number = command_body[i:i + 2]
                number = int.from_bytes(number, byteorder="little")
                subband_bandwidth["channel" + str(ch) + "_subband_bandwidth"] = str(number)
                ch = ch + 1
            return subband_bandwidth

    @staticmethod
    def _decode_reboot_device(command_body):
        if len(command_body) == 0:
            return {'device_rebook': 'OK'}
        else:
            return {}

    @staticmethod
    def _decode_central_frequency_point(command_body):
        """Decodes the central frequency point query command."""
        if len(command_body) < 4:
            return {}
        number = command_body[0:4]
        number = int.from_bytes(number, byteorder="little")

        return {
            "central_frequency_point": str(number / 10000),
        }

    @staticmethod
    def _decode_network_mode_config(command_body):
        """Decodes the network mode config command."""
        if len(command_body) == 0:
            return {}
        return {
            "network_mode_config": command_body[0],
        }

    @staticmethod
    def _decode_delay_target_position(command_body):
        """Decodes the delay target position command."""
        if len(command_body) == 0:
            return {}
        return {
            "delay_target_position": command_body[0],
        }

    @staticmethod
    def _decode_actual_delay_optical_port_1(command_body):
        """Decodes the actual delay optical port 1 command."""
        if len(command_body) == 0:
            return {}
        return {
            "actual_delay_optical_port_1": command_body,
        }

    @staticmethod
    def _decode_actual_delay_optical_port_2(command_body):
        """Decodes the actual delay optical port 2 command."""
        if len(command_body) == 0:
            return {}
        return {
            "actual_delay_optical_port_2": command_body,
        }

    @staticmethod
    def _decode_actual_delay_optical_port_3(command_body):
        """Decodes the actual delay optical port 3 command."""
        if len(command_body) == 0:
            return {}
        return {
            "actual_delay_optical_port_3": command_body,
        }

    @staticmethod
    def _decode_actual_delay_optical_port_4(command_body):
        """Decodes the actual delay optical port 4 command."""
        if len(command_body) == 0:
            return {}
        return {
            "actual_delay_optical_port_4": command_body,
        }

    @staticmethod
    def _decode_optical_port_switch(command_body):
        """Decodes the optical port switch command."""
        if len(command_body) == 0:
            return {}
        return {
            "optical_port_switch": command_body[0],
        }

    @staticmethod
    def _decode_network_mode(command_body):
        """Decodes the network mode command."""
        if len(command_body) == 0:
            return {}
        return {
            "network_mode": command_body[0],
        }

    @staticmethod
    def _decode_mac_address(command_body):
        """Decodes the MAC address command."""
        if len(command_body) == 0:
            return {}
        return {
            "mac_address": command_body.hex(),
        }

    @staticmethod
    def _decode_device_id(command_body):

        """Decodes the opticalportx_mac_topology command."""
        if len(command_body) < 2:
            return {}
        device_id = f"{command_body[0]}.{command_body[1]}"

        return {"device_id": device_id}

    @staticmethod
    def _decode_delay(command_body):
        """Decodes the delay command."""
        if len(command_body) == 0:
            return {}
        return {
            "delay": command_body,
        }

    @staticmethod
    def _decode_gain_compensation(command_body):
        """Decodes the gain compensation command."""
        if len(command_body) == 0:
            return {}
        return {
            "gain_compensation": command_body,
        }

    @staticmethod
    def _decode_optical_port_status(command_body):
        """Decodes the optical port status command."""
        if len(command_body) == 0:
            return {}
        return {
            "optical_port_status": command_body[0],
        }

    @staticmethod
    def _decode_near_end_port_location(command_body):
        """Decodes the near_end_port_location command."""
        if len(command_body) == 0:
            return {}
        return {
            "near_end_port_location": command_body.hex(),
        }

    @staticmethod
    def _decode_channel_0_optical_network_mode(command_body):
        """Decodes the channel_0_optical_network_mode command."""
        if len(command_body) == 0:
            return {}
        return {
            "channel_0_optical_network_mode": command_body[0],
        }

    @staticmethod
    def _decode_channel_1_optical_network_mode(command_body):
        """Decodes the channel_1_optical_network_mode command."""
        if len(command_body) == 0:
            return {}
        return {
            "channel_1_optical_network_mode": command_body[0],
        }

    @staticmethod
    def _decode_optical_module_hardware_parameters(command_body):
        """Decodes the optical_module_hardware_parameters command."""
        if len(command_body) == 0:
            return {}
        return {
            "optical_module_hardware_parameters": command_body.hex(),
        }

    @staticmethod
    def _decode_own_topology_id(command_body):
        """Decodes the own_topology_id command."""
        if len(command_body) == 0:
            return {}
        return {
            "own_topology_id": command_body.hex(),
        }

    @staticmethod
    def _decode_version_number(command_body):

        if len(command_body) == 0:
            return {}
        #    fpga_version_number = int.from_bytes(command_body[:2], byteorder='little')
        #    software_version_number = int.from_bytes(command_body[2:], byteorder='little')

        fpga_data = command_body[:4]
        year = fpga_data[3]
        month = fpga_data[2]
        day = fpga_data[1]
        version_number = fpga_data[0]
        year += 2000
        fpga_version_number = f"Year: {year}, Month: {month}, Day: {day}, Version Number: {version_number}"

        software_data = command_body[4:]
        year = software_data[4]
        month = software_data[3]
        day = software_data[2]
        version_number = software_data[1]
        module_type = software_data[0]
        # Convert module type to string
        if module_type == 0x0a:
            module_type = "near end machine"
        elif module_type == 0x0b:
            module_type = "remote end machine"
        else:
            module_type = "unknown"
            return

        software_version_number = f"Year: {year}, Month: {month}, Day: {day}, Version Number: {version_number}, Module type: {module_type}"
        # Convert year to full year format

        return {'fpga_version_number': fpga_version_number, 'software_version_number': software_version_number}

    @staticmethod
    def _decode_temperature(command_body):
        if len(command_body) == 0:
            return {}
        val = int.from_bytes(command_body, byteorder='little')
        if val > 125000:
            temp = (val * 2 / 1000)
            temp = (int(temp) & 0xff) / 2
        else:
            temp = val / 1000
        return {'temperature': temp}

    @staticmethod
    def _decode_hardware_status(command_body):
        if len(command_body) == 0:
            return {}
        return f"hardware_status: {command_body}"

    @staticmethod
    def _decode_ad5662(command_body):
        if len(command_body) == 0:
            return {}
        parameter = int.from_bytes(command_body[:2], byteorder='little')
        mode = "Automatic" if command_body[2] == 0 else "Manual"
        return f"AD5662: parameter {parameter}, mode {mode}"

    @staticmethod
    def _decode_afc(command_body):
        if len(command_body) == 0:
            return {}
        mode = "Automatic" if command_body[0] == 0 else "Manual"
        automatic_mode_optical_port = command_body[1]
        manual_mode_optical_port = command_body[2]
        return f"AFC: mode {mode}, automatic mode optical port {automatic_mode_optical_port}, manual mode optical port {manual_mode_optical_port}"

    @staticmethod
    def _decode_daatt(command_body):
        if len(command_body) == 0:
            return {}
        channels = [i / 4 for i in command_body]
        return f"DATT: channels {channels}"

    @staticmethod
    def _decode_eth_ip_address(command_body):
        if len(command_body) == 0:
            return {}
        ip_address = ".".join(str(b) for b in command_body)
        return {'eth_ip_address': ip_address}

    @staticmethod
    def _decode_broadband_switching(command_body):
        """Decodes the broadband switching command."""
        if len(command_body) == 0:
            return {}
        working_mode = {
            3: "Channel Mode",
            2: "WideBand Mode",
        }
        return {"working_mode": working_mode.get(command_body[0], "Unknown Mode")}

    @staticmethod
    def _decode_optical_port_devices_connected_1(command_body):
        return {"optical_port_devices_connected_1": Decoder.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def _decode_optical_port_devices_connected_2(command_body):
        return {"optical_port_devices_connected_2": Decoder.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def _decode_optical_port_devices_connected_3(command_body):
        return {"optical_port_devices_connected_3": Decoder.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def _decode_optical_port_devices_connected_4(command_body):
        return {"optical_port_devices_connected_4": Decoder.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def decode_optical_port_devices_connected(command_body):
        if len(command_body) == 0:
            return 0
        return command_body[0]

    @staticmethod
    def _decode_optical_port_device_id_topology_1(command_body):
        device_ids = Decoder.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_1": device_ids}

    @staticmethod
    def _decode_optical_port_device_id_topology_2(command_body):
        device_ids = Decoder.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_2": device_ids}

    @staticmethod
    def _decode_optical_port_device_id_topology_3(command_body):
        device_ids = Decoder.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_3": device_ids}

    @staticmethod
    def _decode_optical_port_device_id_topology_4(command_body):
        device_ids = Decoder.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_4": device_ids}

    @staticmethod
    def decode_optical_port_device_id_topology(command_body):
        """Decodes the opticalportx_topology_id command."""

        if len(command_body) < 2:
            return {}
        port_number = command_body[0]
        device_ids = {}
        id = 1

        for i in range(0, len(command_body), 2):
            device_id = command_body[i] + command_body[i + 1] * 256
            device_ids["id_" + str(id)] = device_id
            id = id + 1
        return device_ids

    @staticmethod
    def _decode_optical_port_mac_topology_1(command_body):
        return {"optical_port_mac_topology_1": Decoder.decode_optical_port_mac_topology(command_body)}

    @staticmethod
    def _decode_optical_port_mac_topology_2(command_body):
        return {"optical_port_mac_topology_2": Decoder.decode_optical_port_mac_topology(command_body)}

    @staticmethod
    def _decode_optical_port_mac_topology_3(command_body):
        return {"optical_port_mac_topology_3": Decoder.decode_optical_port_mac_topology(command_body)}

    @staticmethod
    def _decode_optical_port_mac_topology_4(command_body):
        return {"optical_port_mac_topology_4": Decoder.decode_optical_port_mac_topology(command_body)}

    @staticmethod
    def decode_optical_port_mac_topology(command_body):
        """Decodes the opticalportx_mac_topology command."""
        try:
            body = str(command_body)
            port_number = command_body[0]
            device_macs = {}
            id = 1
            for i in range(0, len(command_body), 4):
                device_mac = command_body[i:i + 4]
                mac_address = ""
                for byte in device_mac:
                    mac_address += f"{byte:02X}:"

                device_macs["mac_" + str(id)] = mac_address
                id = id + 1
            return device_macs
        except IndexError:
            print("Error: The command body is empty.")
            return {}

    @staticmethod
    def _decode_channel_switch(command_body: bytearray) -> dict:
        """Decodes channel status information from the command body."""
        # Check if command body is empty
        if not command_body:
            return {}

        channels = {}
        # Iterate through each byte in the command body
        for i, channel in enumerate(command_body):
            # Determine channel status based on byte value
            status = "ON" if channel == 0 else "OFF"
            # Create channel status key using channel number
            channel_status_key = f"channel_{i + 1}_status"
            # Add channel status to the dictionary
            channels[channel_status_key] = status
        return channels

    @staticmethod
    def _decode_input_and_output_power(command_body):
        if len(command_body) == 0:
            return {}

        downlink_power = Decoder.power_convert(command_body[2:])
        uplink_power = Decoder.power_convert(command_body)
        return {'downlink_output_power': downlink_power, 'uplink_input_power': uplink_power}

    @staticmethod
    def power_convert(command_body):
        if len(command_body) < 2:
            return {}
        data0 = command_body[0]
        data1 = command_body[1]
        value = ((data0 | data1 << 8))
        value = -(value & 0x8000) | (value & 0x7fff)
        uplink_power = value / 256
        uplink_power = round(uplink_power, 2)
        return uplink_power

    @staticmethod
    def optic_module_power_convert(command_body, factor):
        if len(command_body) < 2:
            return {}
        data0 = command_body[0]
        data1 = command_body[1]
        value = (data0 | data1 * 256)
        # Check if the value is negative.
        if value & 0x8000:
            # Convert the value to a negative number.
            value = -(value & 0x7fff)
        power = value * factor
        power = round(power, 2)
        return power





    @staticmethod
    def replace_hex_sequence(data):
        """Searches for the hexadecimal sequence 0x5e5d in a bytearray and replaces it with 0x5d.

        Args:
            data: The bytearray to search and modify.

        Returns:
            The modified bytearray with the replacements made.
        """

        output = bytearray()  # Create a new bytearray to store the modified data
        i = 0
        while i < len(data):
            if i < len(data) - 1 and data[i] == 0x5e and data[i + 1] == 0x5d:
                output.extend(b'\x5e')  # Append 0x5d to the output bytearray
                i += 2  # Skip both bytes of the sequence
            else:
                output.append(data[i])  # Append the current byte to the output
                i += 1
        return output
    @staticmethod
    def _decode_channel_frequency_configuration(command_body):
        if len(command_body) == 0:
            return {}
        command_body = Decoder.replace_hex_sequence(command_body)
        temp = command_body.hex()
        ch = 1
        channels = {}
        for i in range(0, 64, 4):
            number = command_body[i:i + 4].hex()
            number = command_body[i:i + 4]
            number = int.from_bytes(number, byteorder="little")
            channels["channel_" + str(ch) + "_freq"] = str(number / 10000)
            ch = ch + 1
        return channels

    @staticmethod
    def _decode_gain_power_control_att(command_body):
        if len(command_body) < 2:
            return {}
        input_att = command_body[0] / 4
        output_att = command_body[1] / 4
        return {'dlAtt':input_att, 'upAtt': output_att}

    @staticmethod
    def _decode_optical_port_switch(command_body: bytes) -> dict:
        """Decodes optical port switch information from the command body.

        Args:
            command_body: The bytearray containing the command data.

        Returns:
            A dictionary containing optical port activation status information.
        """

        try:
            if not command_body:
                return {}

            parameters = {}
            port_number = 1

            for optical_port_byte in command_body:
                status = "ON" if optical_port_byte == 0 else "OFF"
                parameter_key = f"opt_{port_number}_activation_status"
                parameters[parameter_key] = status
                port_number += 1

            return parameters
        except (TypeError, ValueError):
            raise ValueError(f"Invalid command body for optical port switch: {command_body}")

    @staticmethod
    def _decode_optical_port_status(command_body):
        if len(command_body) == 0:
            return {}
        hex_as_int = command_body[0]
        hex_as_binary = bin(hex_as_int)
        padded_binary = hex_as_binary[2:].zfill(8)
        opt = 1
        temp = []
        for bit in reversed(padded_binary):
            if bit == '0' and opt <= 4:
                temp.append('Connected ')
            elif bit == '1' and opt <= 4:
                temp.append('Disconnected ')
            elif bit == '0' and opt > 4:
                temp.append('Normal')
            elif bit == '1' and opt > 4:
                temp.append('Failure')
            opt = opt + 1
        parameter_dict = dict()

        parameter_dict['opt_1_connection_status'] = temp[0]
        parameter_dict['opt_2_connection_status'] = temp[1]
        parameter_dict['opt_3_connection_status'] = temp[2]
        parameter_dict['opt_4_connection_status'] = temp[3]
        parameter_dict['opt_1_transmission_status'] = temp[4]
        parameter_dict['opt_2_transmission_status'] = temp[5]
        parameter_dict['opt_3_transmission_status'] = temp[6]
        parameter_dict['opt_4_transmission_status'] = temp[7]
        return parameter_dict
