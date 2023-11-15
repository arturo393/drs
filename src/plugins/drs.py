#!/usr/bin/env python3
# -*- coding: iso-8859-15 -*-

# dmu_check_rs485.py  Ejemplo de manejo del puerto serie desde python utilizando la
# libreria multiplataforma pyserial.py (http://pyserial.sf.net)
#
#  Se envia una cadena por el puerto serie y se muestra lo que se recibe
#  Se puede especificar por la linea de comandos el puerto serie a
#  a emplear
#
#  (C)2022 Arturo Veras (arturo@sigma-telecom.com)
#
#
#  LICENCIA GPL
# -----------------------------------------------------------------------------

import sys
from crccheck.crc import Crc16Xmodem
import argparse
# import dru_discovery as discovery
import time
import socket
import json
import requests
import serial
import struct
from enum import IntEnum, Enum

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

fix_ip_start = 0xC0
fix_ip_end = 0x16
fix_ip_end_opt_1 = 0x64
fix_ip_end_opt_2 = 0x78
fix_ip_end_opt_3 = 0x8C
fix_ip_end_opt_4 = 0xA0

SET = 1
QUERY_GROUP = 0
QUERY_SINGLE = 3

ETHERNET = 0
SERIAL = 1

DONWLINK_MODULE = 0 << 7
UPLINK_MODULE = 1 << 7


class DataType(IntEnum):
    DATA_INITIATION = 0x00
    RESPONSE = 0x01
    INTERMEDIATE_FREQUENCY = 0x02
    IF_BOARD_RESPONSE = 0X03


class ResponseFlag(IntEnum):
    SUCCESS = 0x00
    WRONG_COMMAND_NUMBER = 0x01
    COMMAND_DATA_ERROR = 0x02
    COMMAND_BODY_LENGTH_ERROR = 0x03
    OPERATION_FAILED = 0x04
    OTHER_FAILURES = 0X05
    DATA_SIZE_EXCEEDS = 0X06


class HardwarePeripheralDeviceParameterCommand(IntEnum):
    version_number = 0x01
    temperature = 0x02
    hardware_status = 0x03
    ad5662 = 0x05
    afc = 0x07
    datt = 0x09
    vcxo_manual = 0x0e
    vcxo_compensation_enable_step_delay_reference_value = 0x1e
    rx0_broadband_power = 0x20
    rx1_broadband_power = 0x21
    #    q_dac0 = 0x26
    dac1 = 0x28
    _9524 = 0x2a
    _1197a = 0x2c
    _1197b = 0x2e
    test_control_register = 0xca
    eth_ip_address = 0xcc
    module_equipment_number = 0xce
    broadband_switching = 0x81
    reboot_device = 0xd0


class NearEndSettingCommandNumber(IntEnum):
    optical_port_switch = 0x90
    NETWORK_MODE_CONFIG = 0x92
    MAC_ADDRESS = 0x94
    DEVICE_ID = 0x96
    DELAY_TARGET_POSITION = 0x98
    # Add more setting command numbers


class NearEndQueryCommandNumber(IntEnum):
    optical_port_switch = 0x91
    network_mode_config = 0x93
    mac_address = 0x95
    device_id = 0x97
    delay_target_position = 0x99
    optical_port_status = 0x9a
    optical_port_device_id_topology_1 = 0x9b
    actual_delay_optical_port_1 = 0x9c
    optical_port_mac_topology_1 = 0x9d
    optical_port_device_id_topology_2 = 0x9e
    actual_delay_optical_port_2 = 0x9f
    optical_port_mac_topology_2 = 0xa0
    optical_port_device_id_topology_3 = 0xa1
    actual_delay_optical_port_3 = 0xa2
    optical_port_mac_topology_3 = 0xa3
    optical_port_device_id_topology_4 = 0xa4
    actual_delay_optical_port_4 = 0xa5
    optical_port_mac_topology_4 = 0xa6
    optical_module_hw_parameters = 0xa7


# Add more query command numbers
class RemoteQueryCommandNumber(IntEnum):
    # Queries
    optical_port_switch = 0xb1
    network_mode = 0xb3
    mac_address = 0xb5
    device_id = 0xb7
    delay = 0xb9
    gain_compensation = 0xbb
    optical_port_status = 0xbc
    near_end_port_location = 0xbd
    channel_0_optical_network_mode = 0xbe
    channel_1_optical_network_mode = 0xbf
    optical_module_hardware_parameters = 0xc0
    own_topology_id = 0xfe


class RemoteSettingCommandNumber(IntEnum):
    optical_port_switch = 0xb0
    network_mode = 0xb2
    mac_address = 0xb4
    device_id = 0xb6
    delay = 0xb8
    gain_compensation = 0xba


class Rx0QueryCmd(IntEnum):
    broadband_power = 0x20
    channel_frequency_configuration = 0x36
    alc = 0x38
    carrier_search_results = 0x39
    carrier_power_value_after_carrier_search = 0x3a
    compensation_enable_switch = 0x3c
    gain_compensation = 0x3e
    temperature_compensation_table = 0x40
    channel_switch = 0x42
    filter_compensation = 0x43
    frequency_point_compensation = 0x45
    bottom_noise = 0x47
    input_power_peak = 0x49
    alc_control_difference_threshold = 0x4c
    baseband_gain = 0x4e
    central_frequency_point = 0xeb
    subband_bandwidth = 0xed
    bottom_noise_channel_switch = 0xf1
    uplink_noise_suppression_switch = 0xf4
    uplink_noise_suppression_threshold = 0xf6
    uplink_noise_suppression_threshold_correction_value = 0xfc
    mean_exp_search_num = 0x83
    frequency_synchronization_switch = 0x85
    rx0_iir_bandwidth = 0xf6


class Rx0SettingCmd(IntEnum):
    central_frequency_point = 0x22
    channel_frequency_configuration = 0x35
    alc = 0x37
    compensation_enable_switch = 0x3b
    gain_compensation = 0x3d
    temperature_compensation_table = 0x3f
    channel_switch = 0x41
    filter_compensation = 0x43
    frequency_point_compensation = 0x45
    bottom_noise = 0x47
    alc_control_difference_threshold = 0x4b
    baseband_gain = 0x4d
    subband_bandwidth = 0xd0
    bottom_noise_channel_switch = 0xf2
    uplink_noise_suppression_switch = 0xf5
    uplink_noise_suppression_threshold = 0xf7
    uplink_noise_suppression_threshold_correction_value = 0xfd
    mean_exp_search_num = 0x82
    frequency_synchronization_switch = 0x84
    rx0_iir_bandwidth = 0xed


class Tx0QueryCmd:
    compensation_enable_switch = 0x71
    gain_compensation = 0x73
    temperature_compensation_table = 0x75
    filter_compensation = 0x79
    peak_output_power = 0x7a
    downlink_output_power = 0xe5
    gain_power_control_att = 0xef
    power_offset = 0xea
    input_and_output_power = 0xf3


class Tx0SettingCmd:
    compensation_enable_switch = 0x70
    gain_compensation = 0x71
    temperature_compensation_table = 0x74
    filter_compensation = 0x78
    peak_output_power = 0x7a
    gain_power_control_att = 0xe7


class Tx1QueryCmd:
    compensation_enable_switch = 0x80
    gain_compensation = 0x82
    temperature_compensation_table = 0x84
    filter_compensation = 0x88
    peak_output_power = 0x8a
    gain_power_control_att = 0xe8


class Tx1SettingCmd:
    compensation_enable_switch = 0x80
    gain_compensation = 0x82
    temperature_compensation_table = 0x84
    filter_compensation = 0x88
    peak_output_power = 0x8a
    gain_power_control_att = 0xe8


class DRSMasterCommand(IntEnum):
    optical_port_devices_connected_1 = 0xf8
    optical_port_devices_connected_2 = 0xf9
    optical_port_devices_connected_3 = 0xfa
    optical_port_devices_connected_4 = 0xfb
    input_and_output_power = Tx0QueryCmd.input_and_output_power
    channel_switch = Rx0QueryCmd.channel_switch
    channel_frequency_configuration = Rx0QueryCmd.channel_frequency_configuration
    central_frequency_point = Rx0QueryCmd.central_frequency_point
    broadband_switching = HardwarePeripheralDeviceParameterCommand.broadband_switching
    gain_power_control_att = Tx0QueryCmd.gain_power_control_att
    optical_port_switch = NearEndQueryCommandNumber.optical_port_switch
    optical_port_status = NearEndQueryCommandNumber.optical_port_status
    subband_bandwidth = Rx0QueryCmd.subband_bandwidth
    rx0_broadband_power = HardwarePeripheralDeviceParameterCommand.rx0_broadband_power
    rx1_broadband_power = HardwarePeripheralDeviceParameterCommand.rx1_broadband_power
    # optical_module_hw_parameters = NearEndQueryCommandNumber.optical_module_hw_parameters
    # rx0_iir_bandwidth = Rx0QueryCmd.rx0_iir_bandwidth
    temperature = HardwarePeripheralDeviceParameterCommand.temperature


class DRSRemoteCommand(IntEnum):
    temperature = HardwarePeripheralDeviceParameterCommand.temperature
    input_and_output_power = Tx0QueryCmd.input_and_output_power
    channel_switch = Rx0QueryCmd.channel_switch
    channel_frequency_configuration = Rx0QueryCmd.channel_frequency_configuration
    central_frequency_point = Rx0QueryCmd.central_frequency_point
    broadband_switching = HardwarePeripheralDeviceParameterCommand.broadband_switching
    gain_power_control_att = Tx0QueryCmd.gain_power_control_att
    optical_port_switch = NearEndQueryCommandNumber.optical_port_switch
    optical_port_status = NearEndQueryCommandNumber.optical_port_status
    subband_bandwidth = Rx0QueryCmd.subband_bandwidth
    rx0_broadband_power = HardwarePeripheralDeviceParameterCommand.rx0_broadband_power
    rx1_broadband_power = HardwarePeripheralDeviceParameterCommand.rx1_broadband_power
    optical_module_hw_parameters = NearEndQueryCommandNumber.optical_module_hw_parameters
    optical_port_devices_connected_1 = DRSMasterCommand.optical_port_devices_connected_1
    optical_port_devices_connected_2 = DRSMasterCommand.optical_port_devices_connected_2
    optical_port_devices_connected_3 = DRSMasterCommand.optical_port_devices_connected_3
    optical_port_devices_connected_4 = DRSMasterCommand.optical_port_devices_connected_4
    rx0_iir_bandwidth = Rx0QueryCmd.rx0_iir_bandwidth


class DRSRemoteSerialCommand(IntEnum):
    optical_port_device_id_topology_1 = NearEndQueryCommandNumber.optical_port_device_id_topology_1
    optical_port_device_id_topology_2 = NearEndQueryCommandNumber.optical_port_device_id_topology_2
    optical_port_device_id_topology_3 = NearEndQueryCommandNumber.optical_port_device_id_topology_3
    optical_port_device_id_topology_4 = NearEndQueryCommandNumber.optical_port_device_id_topology_4


class DiscoveryCommand(IntEnum):
    optical_port_devices_connected_1 = DRSMasterCommand.optical_port_devices_connected_1
    optical_port_devices_connected_2 = DRSMasterCommand.optical_port_devices_connected_2
    optical_port_devices_connected_3 = DRSMasterCommand.optical_port_devices_connected_3
    optical_port_devices_connected_4 = DRSMasterCommand.optical_port_devices_connected_4
    # eth_ip_address = HardwarePeripheralDeviceParameterCommand.eth_ip_address
    device_id = NearEndQueryCommandNumber.device_id
    optical_port_device_id_topology_1 = NearEndQueryCommandNumber.optical_port_device_id_topology_1
    optical_port_device_id_topology_2 = NearEndQueryCommandNumber.optical_port_device_id_topology_2
    optical_port_device_id_topology_3 = NearEndQueryCommandNumber.optical_port_device_id_topology_3
    optical_port_device_id_topology_4 = NearEndQueryCommandNumber.optical_port_device_id_topology_4
    optical_port_mac_topology_1 = NearEndQueryCommandNumber.optical_port_mac_topology_1
    optical_port_mac_topology_2 = NearEndQueryCommandNumber.optical_port_mac_topology_2
    optical_port_mac_topology_3 = NearEndQueryCommandNumber.optical_port_mac_topology_3
    optical_port_mac_topology_4 = NearEndQueryCommandNumber.optical_port_mac_topology_4


class SettingCommand(IntEnum):
    gain_power_control_att = Tx0SettingCmd.gain_power_control_att
    channel_switch = Rx0SettingCmd.channel_switch
    optical_port_switch = NearEndSettingCommandNumber.optical_port_switch
    broadband_switching = 0x80
    channel_frequency_configuration = Rx0SettingCmd.channel_frequency_configuration


class LtelDruCommand(Enum):
    # use the dict keys as the enum member names
    # use the dict values as the associated values
    uplink_att = (0x04, 0x4004)
    downlink_att = (0x04, 0x4104)
    channel_switch = (0x05, 0x160A)
    working_mode = (0x04, 0xEF0B)
    uplink_start_frequency = (0x07, 0x180A)
    downlink_start_frequency = (0x07, 0x190A)
    work_bandwidth = (0x07, 0x1A0A)
    channel_bandwidth = (0x07, 0x1B0A)
    downlink_vswr = (0x04, 0x0605)
    power_amplifier_temperature = (0x04, 0x0105)
    downlink_output_power = (0x04, 0x0605)
    uplink_input_power = (0x04, 0x2505)


class DRU:
    def __init__(self, position, port, device_id, master_hostname, ip_addr, parent):
        self.position = position
        self.port = port
        self.device_id = device_id
        self.hostname = f"dru{device_id}"
        self.master_hostname = master_hostname
        self.ip_addr = ip_addr
        self.parent = parent
        self.name = f"Remote {port}{position}"
        self.comm_type = ""

    def __repr__(self):
        return "DRU()"

    def __str__(self):
        response = ""
        response += f"RU{self.port}{self.position} "
        response += f"hostname: {self.hostname} "
        response += f"ip_addr: {self.ip_addr} "
        return response

    def __eq__(self, other):
        return self.position == other.position and self.port == other.position and self.mac == other.mac and self.sn == other.sn


class Director:
    director_api_login = "admin"
    director_api_password = "Admin.123"

    def __init__(self, master_host):
        self.master_host = master_host

    def deploy(self):
        director_url = "http://" + self.master_host + "/director/config/deploy"
        director_headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(director_url,
                              headers=director_headers,
                              auth=(self.director_api_login, self.director_api_password),
                              verify=False,
                              timeout=1)
        except requests.exceptions.RequestException as e:
            print("no connection")
            sys.exit(0)

        return q

    def create_host(self, director_query: {}, update_query: {}):

        request_url = "http://" + self.master_host + "/director/host"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(director_query),
                              auth=(self.director_api_login, self.director_api_password),
                              verify=False,
                              timeout=1)

            hostname = director_query['object_name']
            if q.status_code == 422:
                request_url = "http://" + self.master_host + "/director/host?name=" + hostname
                q = requests.post(request_url,
                                  headers=headers,
                                  data=json.dumps(update_query),
                                  auth=(self.director_api_login, self.director_api_password),
                                  verify=False,
                                  timeout=1)
                # sys.stderr.write(f"{q.status_code} {q.text}")

        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"CRITICAL - {e}")
            sys.exit(CRITICAL)
        except requests.exceptions.ConnectTimeout as e:
            sys.stderr.write(f"WARNING - {e}")
            sys.exit(WARNING)
        # print(json.dumps(q.json(),indent=2))
        return q

    def modify_service(self, director_query: {}):

        request_url = "http://" + self.master_host + "/director/service?name=Status"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(director_query),
                              auth=(self.director_api_login, self.director_api_password),
                              verify=False,
                              timeout=1)
        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"CRITICAL - {e}")
            sys.exit(CRITICAL)
        except requests.exceptions.ConnectTimeout as e:
            sys.stderr.write(f"WARNING - {e}")
            sys.exit(WARNING)
        # print(json.dumps(q.json(),indent=2))
        return q

    def create_dru_host(self, dru: DRU, comm_type: int, type: int, imports, device):

        director_query = {
            'object_name': dru.hostname,
            "object_type": "object",
            "address": dru.ip_addr,
            "imports": imports,
            "display_name": dru.name,
            "vars": {
                "opt": str(dru.port),
                "dru": str(dru.position),
                "parents": [dru.parent],
                "device": device,
                "comm_type": str(comm_type),
                "type": str(type)
            }
        }

        request_url = "http://" + self.master_host + "/director/host"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(director_query),
                              auth=(self.director_api_login, self.director_api_password),
                              verify=False,
                              timeout=1)
            # sys.stderr.write(f"{q.status_code} {q.text}")

            # parent = hostname if connected == 1 else dru_connected[f"opt{opt}"][connected - 2].hostname

            if q.status_code == 422:
                update_query = {
                    "object_type": "object",
                    "address": dru.ip_addr,
                    "imports": imports,
                    "vars": {
                        "opt": str(dru.port),
                        "dru": str(dru.position),
                        "parents": [dru.parent],
                        "device": "dru",
                        "comm_type": str(comm_type)

                    }
                }
                request_url = "http://" + self.master_host + "/director/host?name=" + dru.hostname
                q = requests.post(request_url,
                                  headers=headers,
                                  data=json.dumps(update_query),
                                  auth=(self.director_api_login, self.director_api_password),
                                  verify=False,
                                  timeout=1)
                # sys.stderr.write(f"{q.status_code} {q.text}")

        except requests.exceptions.RequestException as e:
            sys.stderr.write(f"CRITICAL - {e}")
            sys.exit(CRITICAL)
        except requests.exceptions.ConnectTimeout as e:
            sys.stderr.write(f"WARNING - {e}")
            sys.exit(WARNING)
        # print(json.dumps(q.json(),indent=2))
        return q


class CommandData:

    def __init__(self):
        self.reply_command_data = None
        self.reply = None
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
        self.message = None
        self.decoder = Decoder()

    def generate_ltel_comunication_board_frame(self, dru_id, cmd_name):

        unknown1 = 0x0101
        site_number = 0
        self.dru_id = dru_id
        unknown2 = 0x0100
        tx_rx = 0x80
        unknown3 = 0x01
        message_type = 0x02
        tx_rx2 = 0xFF
        length = cmd_name.value[0]
        code = cmd_name.value[1]
        data = "".zfill(length * 2)
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
            f"{length:02X}"
            f"{code:04X}"
            f"{data}"
        )

        crc = self.generate_checksum(cmd_unit)
        self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"

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
    def _decode_uplink_att(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "uplink_att": command_body,
        }

    @staticmethod
    def _decode_downlink_att(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "downlink_att": command_body,
        }

    @staticmethod
    def _decode_channel_switch(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "downlink_channel_switch ": command_body,
        }

    @staticmethod
    def _decode_working_mode(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "working_mode ": command_body,
        }

    @staticmethod
    def _decode_uplink_start_frequency(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "uplink_start_frequency  ": command_body,
        }

    @staticmethod
    def _decode_downlink_start_frequency(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "downlink_start_frequency   ": command_body,
        }

    @staticmethod
    def _decode_work_bandwidth(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "work_bandwidth    ": command_body,
        }

    @staticmethod
    def _decode_channel_bandwidth(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "channel_bandwidth     ": command_body,
        }

    @staticmethod
    def _decode_downlink_vswr(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "downlink_vswr      ": command_body,
        }

    @staticmethod
    def _decode_power_amplifier_temperature(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "power_amplifier_temperature      ": command_body,
        }

    @staticmethod
    def _decode_downlink_output_power(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "downlink_output_power      ": command_body,
        }

    @staticmethod
    def _decode_uplink_input_power(command_body):
        """Decodes uplink attenuation value in dbBm"""
        if len(command_body) < 2:
            return {}
        return {
            "uplink_input_power       ": command_body,
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
        return {"workingMode": working_mode.get(command_body[0], "Unknown Mode")}

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
        return Decoder.decode_optical_port_mac_topology(command_body)

    @staticmethod
    def _decode_optical_port_mac_topology_2(command_body):
        return Decoder.decode_optical_port_mac_topology(command_body)

    @staticmethod
    def _decode_optical_port_mac_topology_3(command_body):
        return Decoder.decode_optical_port_mac_topology(command_body)

    @staticmethod
    def _decode_optical_port_mac_topology_4(command_body):
        return Decoder.decode_optical_port_mac_topology(command_body)

    @staticmethod
    def decode_optical_port_mac_topology(command_body):
        """Decodes the opticalportx_mac_topology command."""
        try:
            port_number = command_body[0]
            device_macs = {}
            id = 1
            for i in range(1, len(command_body), 4):
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
    def _decode_channel_switch(command_body):
        if len(command_body) == 0:
            return {}
        i = 1
        channels = {}
        for channel in command_body:
            status = "ON" if channel == 0 else "OFF"
            channels["channel" + str(i) + "Status"] = status
            i = i + 1
        return channels

    @staticmethod
    def _decode_input_and_output_power(command_body):
        if len(command_body) == 0:
            return {}

        downlink_power = Decoder.power_convert(command_body[2:])
        uplink_power = Decoder.power_convert(command_body)
        return {'dlOutputPower': str(downlink_power), 'ulInputPower': str(uplink_power)}

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
    def _decode_channel_frequency_configuration(command_body):
        if len(command_body) == 0:
            return {}
        ch = 1
        channels = {}
        for i in range(0, 64, 4):
            number = command_body[i:i + 4]
            number = int.from_bytes(number, byteorder="little")
            channels["channel" + str(ch) + "ulFreq"] = str(number / 10000)
            channels["channel_" + str(ch) + "_freq"] = str(number / 10000)
            ch = ch + 1
        return channels

    @staticmethod
    def _decode_gain_power_control_att(command_body):
        if len(command_body) < 2:
            return {}
        input_att = command_body[0] / 4
        output_att = command_body[1] / 4
        return {'dlAtt': str(output_att), 'ulAtt': str(input_att)}

    @staticmethod
    def _decode_optical_port_switch(command_body):
        if len(command_body) == 0:
            return {}
        message = ""
        port = 1
        parameter = {}
        for opt_port in command_body:
            status = "ON" if opt_port == 0 else "OFF"
            key = "opt" + str(port) + "ActivationStatus"
            parameter[key] = status
            port = port + 1
        return parameter

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

        parameter_dict['opt1ConnectionStatus'] = temp[0]
        parameter_dict['opt2ConnectionStatus'] = temp[1]
        parameter_dict['opt3ConnectionStatus'] = temp[2]
        parameter_dict['opt4ConnectionStatus'] = temp[3]
        parameter_dict['opt1TransmissionStatus'] = temp[4]
        parameter_dict['opt2TransmissionStatus'] = temp[5]
        parameter_dict['opt3TransmissionStatus'] = temp[6]
        parameter_dict['opt4TransmissionStatus'] = temp[7]
        return parameter_dict


class Command:
    list = list()
    tcp_port = 65050
    udp_port = 65055
    remote_port = 65053

    def __init__(self, args):

        self.cmd_number_ok = None
        self.serial = None
        self.parameters = self.blank_parameter()
        self.set_args(args)

    def set_args(self, args):
        self.parameters['address'] = args['address']
        self.parameters['device'] = args['device']
        self.parameters['hostname'] = args['hostname']
        self.parameters['cmd_type'] = args['cmd_type']
        self.parameters['cmd_data'] = args['cmd_data']
        self.parameters['cmd_name'] = int(args['cmd_name'])

        self.parameters['cmd_body_length'] = int(args['cmd_body_length'])
        self.parameters['device_number'] = int(args['device_number'])
        self.parameters['optical_port'] = int(args['optical_port'])
        self.parameters['work_bandwidth'] = int(args['bandwidth'])
        self.parameters['warning_uplink_threshold'] = int(args['warning_uplink_threshold'])
        self.parameters['critical_uplink_threshold'] = int(args['critical_uplink_threshold'])
        self.parameters['critical_uplink_threshold'] = int(args['critical_uplink_threshold'])
        self.parameters['critical_uplink_threshold'] = int(args['critical_uplink_threshold'])
        self.parameters['warning_temperature_threshold'] = int(args['warning_temperature_threshold'])
        self.parameters['critical_temperature_threshold'] = int(args['critical_temperature_threshold'])

    def create_command(self, cmd_type):
        cmd_type_map = dict(
            single_set=self.create_single_command,
            single_query=self.create_single_command,
            group_query=self.create_group_query_command
        )
        if cmd_type in cmd_type_map:
            get_command = cmd_type_map.get(cmd_type)
            is_created = get_command()
            return is_created
        else:
            return -1

    def create_single_command(self):
        """Generates a single command frame.

        Returns:
            int: The length of the command frame, in bytes.
        """

        cmd_data = CommandData()
        frame_len = cmd_data.generate_ifboard_frame(
            command_number=self.get_command_value(),
            command_body_length=self.parameters['cmd_body_length'],
            command_data=self.parameters['cmd_data'],
        )

        if frame_len > 0:
            self.list.append(cmd_data)

        return frame_len if frame_len > 0 else -2

    def create_group_query_command(self):
        """Creates a group query for the given device.

        Returns:
            int: The number of commands in the group query.
        """
        cmd_name_map = dict(
            dmu_ethernet=DRSMasterCommand,
            dru_ethernet=DRSRemoteCommand,
            discovery_ethernet=DiscoveryCommand
        )
        device = self.parameters['device']
        if device in cmd_name_map:
            cmd_name_group = cmd_name_map[device]
            if cmd_name_group == LtelDruCommand:
                for cmd_name in cmd_name_group:
                    opt = self.parameters['optical_port']
                    dru = self.parameters['device_number']
                    code = cmd_name
                    dru_id = f"{opt}{dru}"
                    cmd_data = CommandData()
                    cmd_data.generate_ltel_comunication_board_frame(dru_id=dru_id, cmd_name=cmd_name)
                    if cmd_data.query != "":
                        self.list.append(cmd_data)
            else:
                for cmd_name in cmd_name_group:
                    cmd_data = CommandData()
                    frame_len = cmd_data.generate_ifboard_frame(
                        command_number=cmd_name,
                        command_body_length=0x00,
                        command_data=-1
                    )
                    if frame_len > 0:
                        self.list.append(cmd_data)

            return len(self.list)
        else:
            return -3

    def create_single_set(self):
        command_number = self.get_command_value()
        command_body_length = self.parameters['command_body_length']
        command_data = self.parameters['command_data']
        cmd_data = CommandData()
        frame_len = cmd_data.generate_ifboard_frame(
            command_number=command_number,
            command_body_length=command_body_length,
            command_data=command_data,
        )
        if frame_len > 0:
            self.list.append(cmd_data)
        return frame_len

    def get_setting_command_value(self, int_number):
        for command in SettingCommand:
            if command.value == int_number:
                return command
        return None

    def get_command_value(self):
        int_number = self.parameters['cmd_name']

        for command in SettingCommand:
            if command.value == int_number:
                return command
        for command in NearEndQueryCommandNumber:
            if command.value == int_number:
                return command
        for command in HardwarePeripheralDeviceParameterCommand:
            if command.value == int_number:
                return command
        for command in RemoteQueryCommandNumber:
            if command.value == int_number:
                return command
        return None

    def transmit_and_receive_tcp(self, address):
        rt = time.time()
        reply_counter = 0
        exception_message = "CRITICAL - "
        for cmd_name in self.list:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((address, self.tcp_port))
                    sock.settimeout(2)
                    data_bytes = bytearray.fromhex(cmd_name.query)
                    sock.sendall(data_bytes)
                    data_received = sock.recv(1024)
                    sock.close()
                    cmd_name.reply = data_received
                    reply_counter = reply_counter + 1
            except Exception as e:
                return 0

        rt = str(time.time() - rt)
        self.parameters['rt'] = rt
        return self.parameters

    def transmit_and_receive_serial(self, port, baud):
        rt = time.time()
        self.serial = self.setSerial(port, baud)
        self.cmd_number_ok = 0
        for cmd_name in self.list:
            self.write_serial_frame(cmd_name.query)
            query_time = time.time()
            data_received = self.read_serial_frame()
            cmd_name.reply = data_received
            if cmd_name.reply != "":
                self.cmd_number_ok = self.cmd_number_ok + 1
            tmp = time.time() - query_time
            time.sleep(tmp)
        self.serial.close()
        rt = str(time.time() - rt)
        self.parameters['rt'] = rt
        return self.cmd_number_ok

    def write_serial_frame(self, Trama):
        cmd_bytes = bytearray.fromhex(Trama)
        hex_byte = ''
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte))
            self.serial.write(bytes.fromhex(hex_byte))
        self.serial.flush()

    def read_serial_frame(self):
        hexadecimal_string = ''
        rcv_hex_array = list()
        is_data_ready = False
        rcv_count = 0
        count = 2
        while not is_data_ready and count > 0:
            try:
                response = self.serial.read()
            except serial.SerialException as e:

                return bytearray()
            rcv_hex = response.hex()
            if rcv_count == 0 and rcv_hex == '7e':
                rcv_hex_array.append(rcv_hex)
                hexadecimal_string = hexadecimal_string + rcv_hex
                rcv_count = rcv_count + 1
            elif rcv_count > 0 and rcv_hex_array[0] == '7e' and (rcv_count == 1 and rcv_hex == '7e') is not True:
                rcv_hex_array.append(rcv_hex)
                hexadecimal_string = hexadecimal_string + rcv_hex
                rcv_count = rcv_count + 1
                if rcv_hex == '7e' or rcv_hex == '7f':
                    is_data_ready = True
                elif rcv_count > 100:
                    return ""
            elif rcv_hex == '':
                self.write_serial_frame('7E')
                return ""
        if count == 0:
            return ""

        self.serial.reset_input_buffer()
        hexResponse = bytearray.fromhex(hexadecimal_string)
        return hexResponse

    def extract_and_decode_received(self) -> int:
        """Extracts and decodes the received commands.

        Returns:
            The number of decoded commands.
        """
        decoded_commands = 0
        for command in self.list:
            if command.reply is None:
                command.reply_command_data = None
                command.message = None
                continue

            if command.command_number in LtelDruCommand:
                decoded_commands += self._decode_ltel_command(command)
            else:
                decoded_commands += self._decode_ifboard_command(command)

            # Update the parameters with the decoded data.
            if command.message:
                self.parameters.update(command.message)

        return decoded_commands

    def _decode_ifboard_command(self, command: CommandData) -> int:

        if len(command.reply) == 0:
            return 0

        module_function_index = 1
        data_type_index = 3
        cmd_number_index = 4
        respond_flag_index = 5
        cmd_body_length_index = 6
        cmd_data_index = 7
        module_function = command.reply[module_function_index]
        data_type = command.reply[data_type_index]
        command_number = command.reply[cmd_number_index]
        if command_number == command.command_number.value:
            response_flag = command.reply[respond_flag_index]
            command_body_length = command.reply[cmd_body_length_index]
            command_body = command.reply[cmd_data_index:cmd_data_index + command_body_length]
            if response_flag == ResponseFlag.SUCCESS:
                command.reply_command_data = command_body
                command.message = command.decoder.ifboard_decode(command.command_number, command_body)
                return 1
            else:
                return 0
        else:
            return 0

    def _decode_ltel_command(self, command: CommandData) -> int:
        """Decodes a LtelDru command.

        Args:
            command: The command to decode.

        Returns:
            The number of decoded commands.
        """

        module_function_index = 1
        data_type_index = 3
        cmd_number_index = 4
        respond_flag_index = 5
        cmd_body_length_index = 14
        cmd_data_index = 17
        response_flag = command.reply[respond_flag_index]
        command_body_length = command.reply[cmd_body_length_index] - 3
        command_body = command.reply[cmd_data_index:cmd_data_index + command_body_length]
        if response_flag == ResponseFlag.SUCCESS:
            command.reply_command_data = command_body
            command.message = Decoder.ltel_decode(command.command_number, command.command_data)
            return 1
        else:
            return 0

    def blank_parameter(self):
        parameters = {}
        dru_parameters = {'dlOutputPower': 100.0, 'ulInputPower': 100.0, 'temperature': '-', 'dlAtt': '-', 'ulAtt': '-',
                          'vswr': '-', 'workingMode': '-', 'mac': '-', 'sn': '-', "Uplink Start Frequency": '-',
                          "Downlink Start Frequency": '-'}

        dmu_parameters = {'optical_port_devices_connected_1': "-", 'optical_port_devices_connected_2': "-",
                          'optical_port_devices_connected_3': "-",
                          'optical_port_devices_connected_4': "-", 'opt1ConnectionStatus': "-",
                          'opt2ConnectionStatus': "-",
                          'opt3ConnectionStatus': "-", 'opt4ConnectionStatus': "-", 'opt1TransmissionStatus': "-",
                          'opt2TransmissionStatus': "-", 'opt3TransmissionStatus': "-", 'opt4TransmissionStatus': "-",
                          'dlOutputPower': 100.0, 'ulInputPower': 100.0, 'ulAtt': "-", 'dlAtt': "-", 'workingMode': "-",
                          'opt1ActivationStatus': '-', 'opt2ActivationStatus': '-', 'opt3ActivationStatus': '-',
                          'opt4ActivationStatus': '-', "Uplink Start Frequency": '-', "Downlink Start Frequency": '-',
                          'temperature': '-', 'central_frequency_point': '-', 'device_id': "-"}

        channel_parameters = self.blank_channel_dict()

        parameters.update(dru_parameters)
        parameters.update(dmu_parameters)
        parameters.update(channel_parameters)
        return parameters

    def blank_channel_dict(self):
        parameters = {}
        channel = 1
        while channel <= 16:
            parameters["channel" + str(channel) + "Status"] = "-"
            parameters["channel" + str(channel) + "ulFreq"] = "-"
            parameters["channel" + str(channel) + "dlFreq"] = "-"
            parameters["channel_" + str(channel) + "_freq"] = "-"
            channel += 1
        return parameters

    def setSerial(self, port, baudrate):
        for times in range(3):
            try:
                s = serial.Serial(port, baudrate)
                s.timeout = 0.1
                s.exclusive = True
                return s

            except serial.SerialException as e:
                time.sleep(1)
                if times == 2:
                    sys.stderr.write("CRITICAL - " + (e.args.__str__()) + str(port))
                    sys.exit(CRITICAL)


class HtmlTable:

    def __init__(self, parameters):
        self.parameters = parameters

    def display(self):
        # device_table = dmu_table(parameters) if device == 'dmu' else dru_table(parameters)
        device_table = self.if_board_table()
        channel_table = self.get_channel_freq_table()
        table = ""
        table += '<div class="sigma-container">'
        table += device_table + channel_table
        table += "</div>"
        return table

    def dru_table(self):
        power_att_table = self.get_power_table()
        vswr_temperature_table = self.get_vswr_temperature_table()
        return power_att_table + vswr_temperature_table

    def dmu_table(self):
        opt_status_table = self.get_opt_status_table()
        power_table = self.get_power_table()
        return opt_status_table + power_table

    def if_board_table(self):
        opt_status_table = self.get_opt_status_table()
        power_att_table = self.get_power_table()
        vswr_temperature_table = self.get_vswr_temperature_table()
        return opt_status_table + power_att_table + vswr_temperature_table

    def get_channel_table(self):
        if self.parameters['workingMode'] == 'Channel Mode':
            table3 = "<table width=80% >"
            table3 += "<thead><tr style=font-size:11px>"
            table3 += "<th width='10%'>Channel</font></th>"
            table3 += "<th width='10%'>Status</font></th>"
            table3 += "<th width='40%'>UpLink [Mhz]</font></th>"
            table3 += "<th width='40%'>Downlink [Mhz]</font></th>"
            table3 += "</tr></thead><tbody>"
            for i in range(1, 17):
                channel = str(i)
                table3 += "<tr align=\"center\" style=font-size:11px>"
                table3 += "<td>" + channel + "</td>"
                table3 += "<td>" + self.parameters["channel" + str(channel) + "Status"] + "</td>"
                table3 += "<td>" + self.parameters["channel" + str(channel) + "ulFreq"] + "</td>"
                table3 += "<td>" + self.parameters["channel" + str(channel) + "dlFreq"] + "</td>"
                table3 += "</tr>"
        else:
            table3 = "<table width=80%>"
            table3 += "<thead><tr style=font-size:12px>"
            table3 += "<th width='40%'>Status</font></th>"
            table3 += "<th width='10%'>Work Bandwidth [Mhz]</font></th>"
            table3 += "<th width='40%'>UpLink [Mhz]</font></th>"
            table3 += "<th width='40%'>Downlink [Mhz]</font></th>"
            table3 += "</tr></thead><tbody>"
            table3 += "<tr align=\"center\" style=font-size:12px>"
            table3 += "<td>" + self.parameters['workingMode'] + "</td>"

            table3 += "<td>" + self.parameters['work_bandwidth'] + "</td>"
            table3 += "<td>" + self.parameters['Uplink Start Frequency'] + "</td>"
            table3 += "<td>" + self.parameters['Downlink Start Frequency'] + "</td>"

            table3 += "</tr>"

        table3 += "</tbody></table>"
        return table3

    def get_power_table(self):
        table2 = "<table width=250>"
        table2 += "<thead>"
        table2 += "<tr  align=\"center\" style=font-size:12px>"
        table2 += "<th width='12%'>Link</font></th>"
        table2 += "<th width='33%'>Power</font> </th>"
        table2 += "<th width='35%'>Attenuation</font></th>"
        table2 += "</tr>"
        table2 += "</thead>"
        table2 += "<tbody>"
        table2 += "<tr align=\"center\" style=font-size:12px><td>Uplink</td><td>" + self.parameters[
            'ulInputPower'] + " [dBm]</td><td>" + self.parameters['ulAtt'] + " [dB]</td></tr>"
        table2 += "<tr align=\"center\" style=font-size:12px><td>Downlink</td><td>" + self.parameters[
            'dlOutputPower'] + " [dBm]</td><td>" + self.parameters['dlAtt'] + " [dB]</td></tr>"
        table2 += "</tbody></table>"
        return table2

    def get_opt_status_table(self):
        device = self.parameters["device"]
        table1 = "<table width=280>"
        table1 += "<thead>"
        table1 += "<tr align=\"center\" style=font-size:12px>"
        table1 += "<th width='12%'>Port</font></th>"
        table1 += "<th width='22%'>Activation Status</font></th>"
        table1 += "<th width='22%'>Connected Remotes</font></th>"
        table1 += "<th width='20%'>Transmission Status</font></th>"
        table1 += "</tr>"
        table1 += "</thead>"
        table1 += "<tbody>"

        for i in range(1, 5):
            connected_name = "optical_port_devices_connected_"
            opt = str(i)
            if not (device == "dru" and (opt == "3" or opt == "4")):
                connected = str(self.parameters[f"{connected_name}{opt}"])
                table1 += "<tr align=\"center\" style=font-size:12px>"
                table1 += "<td>opt" + opt + "</td>"
                table1 += "<td>" + self.parameters['opt' + opt + 'ActivationStatus'] + "</td>"
                table1 += "<td>" + connected + "</td>"
                table1 += "<td>" + self.parameters['opt' + opt + 'TransmissionStatus'] + "</td>"
                table1 += "</tr>"

        table1 += "</tbody>"
        table1 += "</table>"
        return table1

    def get_channel_freq_table(self):
        table3 = "<table width=90%>"
        table3 += "<thead><tr style=font-size:11px>"
        table3 += "<th width='10%'>Channel</font></th>"
        table3 += "<th width='10%'>Status</font></th>"
        table3 += "<th width='40%'>UpLink Frequency [Mhz]</font></th>"
        table3 += "<th width='40%'>Downlink Frequency [Mhz]</font></th>"
        table3 += "</tr></thead><tbody>"

        if (self.parameters['workingMode'] == 'Channel Mode'):
            table3 = "<table width=100%>"
            table3 += "<thead><tr style=font-size:11px>"
            table3 += "<th width='5%'>Channel</font></th>"
            table3 += "<th width='5%'>Status</font></th>"
            #        table3 += "<th width='50%'>UpLink [Mhz]</font></th>"
            table3 += "<th width='50%'>Downlink [Mhz]</font></th>"
            table3 += "</tr></thead><tbody>"
            for i in range(1, 17):
                channel = str(i)
                table3 += "<tr align=\"center\" style=font-size:12px>"
                table3 += "<td>" + channel + "</td>"
                table3 += "<td>" + self.parameters["channel" + str(channel) + "Status"] + "</td>"
                table3 += "<td>" + self.parameters["channel_" + str(channel) + "_freq"] + "</td>"
                #            table3 += "<td>" + parameter_dic["channel" + str(channel) + "ulFreq"] + "</td>"
                #            table3 += "<td>" + parameter_dic["channel" + str(channel) + "dlFreq"] + "</td>"
                table3 += "</tr>"
        else:
            table3 = "<table width=90%>"
            table3 += "<thead><tr style=font-size:12px>"
            table3 += "<th width='10%'>Mode</font></th>"
            table3 += "<th width='30%'>Work Bandwidth [Mhz]</font></th>"
            table3 += "<th width='30%'>Central Frequency Point [Mhz]</font></th>"
            #       table3 += "<th width='30%'>Downlink [Mhz]</font></th>"
            table3 += "</tr></thead><tbody>"
            table3 += "<tr align=\"center\" style=font-size:12px>"
            table3 += "<td>" + self.parameters['workingMode'] + "</td>"
            table3 += "<td>" + str(self.parameters["work_bandwidth"]) + "</td>"
            # table3 += "<td>" + parameter_dic['Uplink Start Frequency'] + "</td>"
            # table3 += "<td>" + parameter_dic['Downlink Start Frequency'] + "</td>"
            table3 += "<td>" + self.parameters['central_frequency_point'] + "</td>"

        table3 += "</tbody></table>"
        return table3

    def get_vswr_temperature_table(self):
        temperature = str(self.parameters['temperature'])
        table2 = "<table width=90%>"
        table2 += "<thead>"
        table2 += "<tr  style=font-size:12px>"
        table2 += "<th width='40%'>Temperature</font></th>"
        #        table2 += "<th width='40%'>VSWR</font></th>"
        table2 += "</tr>"
        table2 += "</thead>"
        table2 += "<tbody>"
        table2 += "<tr align=\"center\" style=font-size:12px>"
        table2 += "<td>" + temperature + " [&deg;C] </td> "
        #        table2 += "<td>" + self.parameters['vswr'] + "</td>"
        table2 += "</tr>"
        table2 += "</tbody></table>"
        return table2


class Graphite:
    def __init__(self, parameters):
        self.parameters = parameters

    def display(self):
        graphite = ""
        if self.parameters['device'] == 'dmu_ethernet':
            graphite = self.dmu_output()
        elif self.parameters['device'] == 'dru_ethernet':
            graphite = self.dru_output()
        elif self.parameters['device'] == 'discovery_ethernet' or self.parameters['device'] == 'discovery_serial':
            graphite = self.discovery_output()
        elif self.parameters['device'] == 'dmu_serial':
            if self.parameters['cmd_type'] == 'single_query':
                graphite = self.dmu_serial_single()
            elif self.parameters['cmd_type'] == 'group_query':
                graphite = self.dmu_output()
        elif self.parameters['device'] == 'dru_serial_host':
            if self.parameters['cmd_type'] == 'single_query':
                graphite = self.dmu_serial_single()
        else:
            graphite = ""
        return graphite

    def dru_output(self):
        graphite = ""
        if self.parameters['dlOutputPower'] == 0.0:
            self.parameters['dlOutputPower'] = "-"
        else:
            self.parameters['dlOutputPower'] = str(self.parameters['dlOutputPower'])
        pa_temperature = "Temperature=" + str(self.parameters['temperature'])
        pa_temperature += ";" + str(self.parameters['warning_temperature_threshold'])
        pa_temperature += ";" + str(self.parameters['critical_temperature_threshold'])
        dl_str = f"Downlink={self.parameters['dlOutputPower']}"
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        vswr = "VSWR=" + self.parameters['vswr']
        up_str = f"Uplink={self.parameters['ulInputPower']}"
        up_str += ";" + str(self.parameters['warning_uplink_threshold'])
        up_str += ";" + str(self.parameters['critical_uplink_threshold'])
        rt = "RT=" + self.parameters['rt'] + ";1000;2000"
        graphite = rt + " " + pa_temperature + " " + dl_str + " " + vswr + " " + up_str
        return graphite

    def dmu_output(self):

        graphite = ""
        dl_str = f"Downlink={self.parameters['dlOutputPower']}"
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        temperature_str = "Temperature=" + str(self.parameters['temperature'])
        temperature_str += ";" + str(self.parameters['warning_temperature_threshold'])
        temperature_str += ";" + str(self.parameters['critical_temperature_threshold'])
        graphite = dl_str + " " + temperature_str
        return graphite

    def discovery_output(self):
        rt = self.parameters['rt']
        dt = self.parameters['dt']
        rt_str = "RT=" + rt
        rt_str += ";" + str(1)
        rt_str += ";" + str(1)
        dt_str = "DT=" + dt
        dt_str += ";" + str(2)
        dt_str += ";" + str(2)
        graphite = rt_str + " " + dt_str
        return graphite

    def dmu_serial_single(self):
        graphite = ""
        rt_str = "RTA=" + self.parameters['rt'] + ";1000;2000"
        graphite = rt_str + " "
        return graphite


class Alarm:

    def __init__(self, parameters):
        self.parameters = parameters

    def display(self):

        if self.parameters['dlOutputPower'] != '-':
            dlPower = float(self.parameters['dlOutputPower'])
        else:
            dlPower = -200
        if self.parameters['ulInputPower'] != '-':
            ulPower = float(self.parameters['ulInputPower'])
        else:
            ulPower = -200
        if self.parameters['temperature'] != '-':
            temperature = float(self.parameters['temperature'])
        else:
            temperature = -200

        alarm = ""

        if dlPower >= self.parameters['critical_uplink_threshold']:
            alarm += "<h3><font color=\"#ff5566\">Downlink Power Level Critical "
            alarm += self.parameters['dlOutputPower']
            alarm += " [dBn]!</font></h3>"

        elif dlPower >= self.parameters['critical_uplink_threshold']:
            alarm += "<h3><font color=\"#ffaa44\">Downlink Power Level Warning "
            alarm += self.parameters['dlOutputPower']
            alarm += "[dBm]</font></h3>"

        if ulPower >= self.parameters['critical_uplink_threshold']:
            alarm += "<h3><font color=\"#ff5566\">Uplink Power Level Critical "
            alarm += self.parameters['ulInputPower']
            alarm += "[dBm]!</font></h3>"

        elif ulPower >= self.parameters['warning_uplink_threshold']:
            alarm += "<h3><font color=\"#ffaa44\">Uplink Power Level Warning "
            alarm += self.parameters['ulInputPower']
            alarm += "[dBm]</font></h3>"

        if temperature >= self.parameters['critical_temperature_threshold']:
            alarm += "<h3><font color=\"#ff5566\">Temperature Level Critical "
            alarm += self.parameters['temperature']
            alarm += " [&deg;C]]!</font></h3>"

        elif temperature >= self.parameters['warning_temperature_threshold']:
            alarm += "<h3><font color=\"#ffaa44\">Temperature Level Warning "
            alarm += self.parameters['temperature']
            alarm += " [&deg;C]]!</font></h3>"

        return alarm


class PluginOutput:
    def __init__(self, parameters):
        self.parameters = parameters
        # Define a dictionary of command types and corresponding functions
        self.command_functions = {
            'dru_serial_service': self.dru_serial_display,
            'dru_serial_host': self.dru_serial_host_display,
            'dmu_serial': self.dmu_serial_host_display,
            'dru_ethernet': self.get_master_remote_service_message,
            'dmu_ethernet': self.get_master_remote_service_message,
            'discovery_ethernet': self.discovery_display,
            'discovery_serial': self.discovery_display
        }

    def dru_serial_display(self):
        # Default values for downlink and uplink power
        default_power = 100.0

        # Get downlink power
        downlink_power = float(self.parameters.get('dlOutputPower', default_power))

        # Get uplink power
        uplink_power = float(self.parameters.get('ulInputPower', default_power))

        # Set default values if the values are '-'
        downlink_power = 100.0 if downlink_power == '-' else downlink_power
        uplink_power = 100.0 if uplink_power == '-' else uplink_power

        graphite = ""
        if downlink_power > 50.0:
            self.parameters['dlOutputPower'] = "-"
        if uplink_power > 50.0:
            self.parameters['ulInputPower'] = "-"

        alarm = Alarm(self.parameters)
        html_table = HtmlTable(self.parameters)
        graphite = Graphite(self.parameters)
        # sys.stderr.write(alarm.display() + html_table.display() + "|" + graphite.display())
        plugin_output_message = str(self.parameters)
        exit_code = WARNING if alarm.display() != "" else OK
        return exit_code, plugin_output_message

    def dru_serial_host_display(self):
        rt = self.parameters['rt']
        device_id = int(self.parameters["hostname"][3:4])
        optical_port = str(self.parameters["optical_port"])
        key_name = f"optical_port_device_id_topology_{optical_port}"
        optical_port_device_id_topology = self.parameters[key_name]
        exit_value = CRITICAL
        message = f"CRITICAL - No id {device_id} found"
        for key, value in optical_port_device_id_topology.items():
            if value == device_id:
                message = f"OK - id {device_id} found"
                exit_value = OK
        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        plugin_output_message = f"{message}, RTA = {rt} ms | {graphite.dmu_serial_single()}"
        exit_code = exit_value
        return exit_code, plugin_output_message

    def dmu_serial_host_display(self):
        rt = self.parameters['rt']
        # for key, value in self.parameters.items():
        #    if value != "-":
        #        sys.stderr.write(f"{key}: {value} \n")

        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        plugin_output_message = f"OK - RTA = {rt} ms | {graphite.display()}"
        exit_code = OK
        return exit_code, plugin_output_message

    def get_master_remote_service_message(self):
        # Default values for downlink and uplink power
        default_power = 100.0
        # Get downlink power
        downlink_power = float(self.parameters.get('dlOutputPower', default_power))
        # Get uplink power
        uplink_power = float(self.parameters.get('ulInputPower', default_power))
        # Set default values if the values are '-'
        downlink_power = 100.0 if downlink_power == 100.0 else downlink_power
        uplink_power = 100.0 if uplink_power == 100.0 else uplink_power
        graphite = ""
        if downlink_power > 50.0:
            self.parameters['dlOutputPower'] = "-"
        if uplink_power > 50.0:
            self.parameters['ulInputPower'] = "-"
        alarm = Alarm(self.parameters)
        html_table = HtmlTable(self.parameters)
        graphite = Graphite(self.parameters)
        plugin_output_message = f"{alarm.display()}{html_table.display()}|{graphite.display()}"
        exit_code = WARNING if alarm.display() != "" else OK
        if self.parameters['cmd_type'] == 'single_set':
            plugin_output_message = "OK"
        return exit_code, plugin_output_message

    def discovery_display(self):
        rt = self.parameters['rt']
        dt = self.parameters['dt']
        # for key, value in self.parameters.items():
        #    if value != "-":
        #        sys.stderr.write(f"{key}: {value} \n")

        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        dt = round(float(dt), 2)
        plugin_output_message = f"OK - DTA = {dt} ms, RTA = {rt} ms | {graphite.display()}"
        exit_code = OK
        return exit_code, plugin_output_message

    def create_message(self):
        device = self.parameters['device']
        if device in self.command_functions:
            get_message = self.command_functions.get(device)
            exit_code, message = get_message()
            return exit_code, message
        else:
            return WARNING, f"WARNING  - no output message for {device}"


class Discovery:
    def __init__(self, parameters):
        self.parameters = parameters

    def ethernet(self):
        # opt = self.parameters['port']
        dt = time.time()
        device = "dru_ethernet"
        imports = ["ethernet-host-template"]
        hostname = socket.gethostname()
        master_host = socket.gethostbyname(hostname)
        director = Director(master_host)
        dru_connected = self.dru_connected_search()
        deploy = 0
        for opt in dru_connected:
            for dru in dru_connected[opt]:
                director_query = {
                    'object_name': dru.hostname,
                    "object_type": "object",
                    "address": dru.ip_addr,
                    "imports": imports,
                    "display_name": dru.name,
                    "vars": {
                        "opt": str(dru.port),
                        "dru": str(dru.position),
                        "parents": [dru.parent],
                        "device": device,
                    }
                }
                update_query = {
                    "object_type": "object",
                    "address": dru.ip_addr,
                    "imports": imports,
                    "vars": {
                        "opt": str(dru.port),
                        "dru": str(dru.position),
                        "parents": [dru.parent],
                        "device": device,
                    }
                }
                response = director.create_host(director_query=director_query, update_query=update_query)
                message = ""
                if response.status_code == 304:
                    message = "Not modified"
                elif response.status_code == 200:
                    message = "Success"
                else:
                    message = "Unknown"

                # sys.stderr.write(f"{dru} {message} \n")
                if response.status_code != 304:
                    director.deploy()
        self.parameters["dt"] = str(time.time() - dt)

    def dru_connected_search(self):
        hostname = self.parameters['hostname']
        net = self.parameters["device_id"]
        dru_connected = {}
        fix_ip_end_opt = [0, 100, 120, 140, 160]  # You can adjust these values according to your logic
        for opt in range(1, 5):
            port_name = f"optical_port_devices_connected_{opt}"
            dru_connected[f"opt{opt}"] = []
            optical_port_devices_connected = 0 if self.parameters[port_name] == '-' else self.parameters[port_name] + 1
            for connected in range(1, optical_port_devices_connected):
                connected_ip_addr_name = f"optical_port_connected_ip_addr_{opt}{connected}"
                id_key = f"optical_port_device_id_topology_{opt}"
                device_id = self.parameters[id_key][f"id_{connected}"]
                parent = hostname if connected == 1 else dru_connected[f"opt{opt}"][connected - 2].hostname
                ip = f"{fix_ip_start}.{net}.{fix_ip_end_opt[opt] + connected - 1}"  # You can use a list to store the different values of fix_ip_end_opt
                if device_id != 0:
                    d = DRU(connected, opt, device_id, hostname, ip, parent)
                    dru_connected[f"opt{opt}"].append(d)
                    self.parameters[connected_ip_addr_name] = ip
        return dru_connected

    def serial(self):
        # opt = self.parameters['port']
        dt = time.time()
        device = "dru_serial_host"
        imports = ["serial-host-template"]
        cmd_name = "254"
        hostname = socket.gethostname()
        master_host = socket.gethostbyname(hostname)
        director = Director(master_host)
        dru_connected = self.dru_connected_search()
        deploy = 0
        for opt in dru_connected:
            for dru in dru_connected[opt]:
                director_query = {
                    'object_name': dru.hostname,
                    "object_type": "object",
                    "address": dru.ip_addr,
                    "imports": imports,
                    "display_name": dru.name,
                    "vars": {
                        "opt": str(dru.port),
                        "dru": str(dru.position),
                        "parents": [dru.parent],
                        "device": device,
                        "cmd_name": cmd_name
                    }
                }
                update_query = {
                    "object_type": "object",
                    "address": dru.ip_addr,
                    "imports": imports,
                    "vars": {
                        "opt": str(dru.port),
                        "dru": str(dru.position),
                        "parents": [dru.parent],
                        "device": device,
                        "cmd_name": cmd_name
                    }
                }
                response = director.create_host(director_query=director_query, update_query=update_query)
                message = ""
                if response.status_code == 304:
                    message = "Not modified"
                elif response.status_code == 200:
                    director_query = {
                        'object_name': 'Status',
                        "object_type": "object",
                        "vars": {
                            "opt": str(dru.port),
                            "device_number": str(dru.position),
                        }
                    }
                    response = director.modify_service(director_query=director_query)
                    if response.status_code == 304:
                        message = f"{message} - Error - Service modified"
                    elif response.status_code == 200:
                        message = f"{message} - Success - Service modified"
                    else:
                        message = f"{message} - {response.text}"
                else:
                    message = "Unknown"

                sys.stderr.write(f"{dru} {message} \n")
                if response.status_code != 304:
                    director.deploy()
        self.parameters["dt"] = str(time.time() - dt)

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN
