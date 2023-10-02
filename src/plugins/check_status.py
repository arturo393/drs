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
import getopt
from crccheck.crc import Crc16Xmodem
import argparse
# import dru_discovery as discovery
import time
import socket
import json
import requests
from enum import IntEnum

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
QUERY = 0


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


class SettingCommand(IntEnum):
    COMMAND_ERROR_RETURN_TYPE = 0x00
    AD5662 = 0x04
    AFC = 0x06
    DATT = 0x08
    RESTORE_FACTORY_CONFIGURATION = 0x0a
    RESTORING_CONSISTENCY = 0x14
    _5662_TEMPERATURE_COMPENSATION = 0x19
    VCXO_COMPENSATION_ENABLE_STEP_DELAY_REFERENCE_VALUE = 0x1d
    DAC0 = 0x25
    DAC1 = 0x27
    _9524 = 0x29
    _1197A = 0x2b
    _1197B = 0x2d
    TEST_CONTROL_REGISTER = 0xc9
    ETH_IP_ADDRESS = 0xcb
    MODULE_EQUIPMENT_NUMBER = 0x16
    broadband_switching = 0x80


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


class NearEndSettingCommandNumber(IntEnum):
    OPTICAL_PORT_SWITCH = 0x90
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
    optical_module_hw_parameters = NearEndQueryCommandNumber.optical_module_hw_parameters
    rx0_iir_bandwidth = Rx0QueryCmd.rx0_iir_bandwidth
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


class DiscoveryCommand(IntEnum):
    optical_port_devices_connected_1 = DRSMasterCommand.optical_port_devices_connected_1
    optical_port_devices_connected_2 = DRSMasterCommand.optical_port_devices_connected_2
    optical_port_devices_connected_3 = DRSMasterCommand.optical_port_devices_connected_3
    optical_port_devices_connected_4 = DRSMasterCommand.optical_port_devices_connected_4
    eth_ip_address = HardwarePeripheralDeviceParameterCommand.eth_ip_address
    device_id = NearEndQueryCommandNumber.device_id
    optical_port_device_id_topology_1 = NearEndQueryCommandNumber.optical_port_device_id_topology_1
    optical_port_device_id_topology_2 = NearEndQueryCommandNumber.optical_port_device_id_topology_2
    optical_port_device_id_topology_3 = NearEndQueryCommandNumber.optical_port_device_id_topology_3
    optical_port_device_id_topology_4 = NearEndQueryCommandNumber.optical_port_device_id_topology_4


DONWLINK_MODULE = 0 << 7
UPLINK_MODULE = 1 << 7


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

    def __repr__(self):
        return "DRU()"

    def __str__(self):
        response = ""
        response += f"RU{self.port}{self.position} "
        response += f"device_id:{self.device_id} "
        response += f"master_hostname:{self.master_hostname} "
        response += f"hostname: {self.hostname} "
        response += f"ip_addr: {self.ip_addr} "
        response += f"parent:{self.parent}"
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

    def create_dru_host(self, dru: DRU):

        director_query = {
            'object_name': dru.hostname,
            "object_type": "object",
            "address": dru.ip_addr,
            "imports": ["check_status_template"],
            "display_name": dru.name,
            "vars": {
                "opt": str(dru.port),
                "dru": str(dru.position),
                "parents": [dru.parent],
                "device": "dru"

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
                    "imports": ["check_status_template"],
                    "vars": {
                        "opt": str(dru.port),
                        "dru": str(dru.position),
                        "parents": [dru.parent],
                        "device": "dru"

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


def bytearray_to_hex(byte_array):
    hex_string = ''.join(format(byte, '02X') for byte in byte_array)
    return hex_string


def get_checksum(cmd):
    """
    -Description: this fuction calculate the checksum for a given comand
    -param text: string with the data, ex device = 03 , id = 03 cmd = 0503110000
    -return: cheksum for the given command
    """
    data = bytearray.fromhex(cmd)

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

    # Add more query command functions


class CommandData:
    START_FLAG = "7E"
    END_FLAG = "7F"

    def __init__(self, module_address, module_link, module_function, command_number, command_data, command_type,
                 response_flag, command_body_length):

        self.module_address = module_link | module_address
        self.module_function = module_function
        self.command_number = command_number
        self.command_type = command_type
        self.response_flag = response_flag
        self.command_body_length = command_body_length
        self.command_data = command_data
        self.reply = ""
        self.reply_command_data = ""

        if command_number in [cmd_name.value for cmd_name in SettingCommand]:
            cmd_unit = self.cmd_unit_set()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"
        elif command_number in [cmd_name.value for cmd_name in HardwarePeripheralDeviceParameterCommand]:
            cmd_unit = self.cmd_unit_query()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"
        elif command_number in [cmd_name.value for cmd_name in NearEndQueryCommandNumber]:
            cmd_unit = self.cmd_unit_query()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"

        elif command_number in [cmd_name.value for cmd_name in RemoteQueryCommandNumber]:
            cmd_unit = self.cmd_unit_query()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"
        elif command_number in [cmd_name.value for cmd_name in DRSRemoteCommand]:
            cmd_unit = self.cmd_unit_query()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"

        elif command_number in [cmd_name.value for cmd_name in DRSMasterCommand]:
            cmd_unit = self.cmd_unit_query()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"
        elif command_number in [cmd_name.value for cmd_name in DiscoveryCommand]:
            cmd_unit = self.cmd_unit_query()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"


        else:
            self.query = ""

    def __str__(self):
        if self.reply:
            reply = bytearray_to_hex(self.reply)
            message = self.get_reply_message()

        else:
            reply = "No reply"
            message = ""
            decode = ""

        return f"{self.query} -  {reply} - {message}"

    def set_command(self, command_number, command_body_length):
        self.command_number = command_number
        self.command_body_length = command_body_length

    def cmd_unit_query(self):

        cmd_unit = (
            f"{self.module_function:02X}"
            f"{self.module_address:02X}"
            f"{self.command_type:02X}"
            f"{self.command_number:02X}"
            f"{self.response_flag:02X}"
            f"{self.command_body_length:02X}"
        )
        return cmd_unit

    def cmd_unit_set(self):
        command_number = ((self.command_number & 0xFF) << 8) | ((self.command_number >> 8) & 0xFF)
        command_body_length = ((self.command_body_length & 0xFF) << 8) | ((self.command_body_length >> 8) & 0xFF)

        cmd_unit = (
            f"{self.module_function:02X}"
            f"{self.module_address:02X}"
            f"{0:02X}"
            f"{self.command_number:02X}"
            f"{self.response_flag:02X}"
            f"{self.command_body_length:02X}"
            f"{self.command_data:02X}"
        )

        # Generate command_data with specified length
        command_data_str = f"{self.command_data:0{self.command_body_length * 2}X}"
        return f"{cmd_unit}{command_data_str}"

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

    def extract_data(self):
        module_function_index = 1
        data_type_index = 3
        cmd_number_index = 4
        respond_flag_index = 5
        cmd_body_length_index = 6
        cmd_data_index = 7

        if not self.reply:
            self.reply_command_data = ""
            return

        module_function = self.reply[module_function_index]
        data_type = self.reply[data_type_index]
        command_number = self.reply[cmd_number_index]
        response_flag = self.reply[respond_flag_index]
        command_body_length = self.reply[cmd_body_length_index]
        command_body = self.reply[cmd_data_index:cmd_data_index + command_body_length]

        self.reply_command_data = command_body if response_flag == ResponseFlag.SUCCESS else ""


class Settings:
    @staticmethod
    def optical_port_switch(data):
        switch_signal = data[0]
        switch_status = "On" if switch_signal == 0 else "Off"
        return f"Optical Port Switch Status: {switch_status}"

    @staticmethod
    def network_mode_config(data):
        network_mode = data[0]
        configuration = {
            0: "Automatic Switching",
            1: "Selective Light 1",
            2: "Selective Light 2",
            3: "Selective Light 3",
        }
        return f"Network Mode Configuration: {configuration.get(network_mode, 'Unknown')}"
    # Add more setting command functions


class Queries:

    def decode(command_number, command_body):
        """Decodes a command number."""
        try:
            return getattr(Queries, f"_decode_{command_number.name}")(command_body)
        except AttributeError:
            print(f"Command number {command_number:02X} is not supported.")
            return {}

    @staticmethod
    def _decode_optical_module_hw_parameters(array):
        parameters = {}
        step = 8

        # The order of the parameters in the array is:
        #
        #    Fb0_ Temp 4byte temperature
        #    Fb0_ Rx_ Pwr 2byte Received power
        #    Fb0_ Tx_ Pwr 2byte Transmission power
        #    Fb1_ Temp 4byte temperature
        #    Fb1_ Rx_ Pwr 2byte Received power
        #    Fb1_ Tx_ Pwr 2byte Transmission power
        #    Fb2_ Temp 4byte temperature
        #    Fb2_ Rx_ Pwr 2byte Received power
        #    Fb2_ Tx_ Pwr 2byte Transmission power
        #    Fb3_ Temp 4byte temperature
        #    Fb3_ Rx_ Pwr 2byte Received power
        #    Fb3_ Tx_ Pwr 2byte Transmission power

        for i in range(0, len(array), step):
            test = array[i:i + step]
            fb_number = i // step
            temp = array[i:i + 4]
            rx_pwr = array[i + 4:i + 6]
            tx_pwr = array[i + 6:i + step]
            temp = round(int.from_bytes(temp, byteorder="little") * 0.001, 2)
            rx_pwr = Queries.optic_module_power_convert(rx_pwr)
            tx_pwr = Queries.optic_module_power_convert(tx_pwr)
            parameter_name = "Fb{}_Temp".format(
                fb_number,
            )
            parameters[parameter_name] = temp
            parameter_name = "Fb{}_Rx_Pwr".format(
                fb_number,
            )
            parameters[parameter_name] = rx_pwr
            parameter_name = "Fb{}_Tx_Pwr".format(
                fb_number,
            )
            parameters[parameter_name] = tx_pwr

        return parameters

    @staticmethod
    def _decode_rx0_broadband_power(command_body):
        """Decodes the broadband power query command."""
        if len(command_body) < 2:
            return {}

        rx0_broadband_power = Queries.power_convert(command_body)

        return {
            "rx0_broadband_power": rx0_broadband_power,
        }

    @staticmethod
    def _decode_rx1_broadband_power(command_body):
        """Decodes the broadband power query command."""
        if len(command_body) < 2:
            return {}

        rx1_broadband_power = Queries.power_convert(command_body)

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
    def _decode_central_frequency_point(command_body):
        """Decodes the central frequency point query command."""
        if len(command_body) < 0:
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
        status = ["Locked" if i else "Loss of lock" for i in command_body]
        return f"Hardware status: {status}"

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
        return {"optical_port_devices_connected_1": Queries.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def _decode_optical_port_devices_connected_2(command_body):
        return {"optical_port_devices_connected_2": Queries.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def _decode_optical_port_devices_connected_3(command_body):
        return {"optical_port_devices_connected_3": Queries.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def _decode_optical_port_devices_connected_4(command_body):
        return {"optical_port_devices_connected_4": Queries.decode_optical_port_devices_connected(command_body)}

    @staticmethod
    def decode_optical_port_devices_connected(command_body):
        if len(command_body) == 0:
            return "0"
        return command_body[0]

    @staticmethod
    def _decode_optical_port_device_id_topology_1(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_1": device_ids}

    @staticmethod
    def _decode_optical_port_device_id_topology_2(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_2": device_ids}

    @staticmethod
    def _decode_optical_port_device_id_topology_3(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_3": device_ids}

    @staticmethod
    def _decode_optical_port_device_id_topology_4(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return {"optical_port_device_id_topology_4": device_ids}

    @staticmethod
    def decode_optical_port_device_id_topology(command_body):
        """Decodes the opticalportx_topology_id command."""

        if len(command_body) == 0:
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
        return Queries.decode_optical_port_mac_topology(command_body)

    @staticmethod
    def _decode_optical_port_mac_topology_2(command_body):
        return Queries.decode_optical_port_mac_topology(command_body)

    @staticmethod
    def _decode_optical_port_mac_topology_3(command_body):
        return Queries.decode_optical_port_mac_topology(command_body)

    @staticmethod
    def _decode_optical_port_mac_topology_4(command_body):
        return Queries.decode_optical_port_mac_topology(command_body)

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

        downlink_power = Queries.power_convert(command_body[2:])
        uplink_power = Queries.power_convert(command_body)
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
    def optic_module_power_convert(command_body):
        if len(command_body) < 2:
            return {}
        data0 = command_body[0]
        data1 = command_body[1]
        value = (data0 | data1 << 8)
        value = -(value & 0x8000) | (value & 0x7fff)
        power = value * 0.1
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


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


def cmd_help():
    sys.stderr.write("""Uso: check_status [opciones]
    Ejemplo de uso de la consulta por ip
    opciones:
    -a, --address 192.168.11.22
    -d, --device  dmu, dru
    -n, --hostname dmu
    -p, --port 1
    -b, --bandwidth 10
    -l, --cmd_body_length
    -c, --cmd_name
    -cd, --cmd_data
    -hlwu, --highLevelWarningUplink
    -hlcu, --highLevelCriticalUplink
    -hlwd, --highLevelWarningDownlink
    -hlcd, --highLevelCriticalDownlink
    """)


def args_check():
    ap = argparse.ArgumentParser()
    # Add the arguments to the parser
    # ap.add_argument("-h", "--help", required=False,  help="help")
    try:
        ap.add_argument("-a", "--address", required=True, help="address es requerido", default="192.168.11.22")
        ap.add_argument("-d", "--device", required=True, help="device es requerido", default="dmu")
        ap.add_argument("-n", "--hostname", required=True, help="hostname es requerido", default="dmu0")
        ap.add_argument("-p", "--port", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-b", "--bandwidth", required=True, help="bandwidth es requerido", default="0")
        ap.add_argument("-l", "--cmd_body_length", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-c", "--cmd_name", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-cd", "--cmd_data", required=False, help="bandwidth es requerido", default="0")
        ap.add_argument("-t", "--type", required=False, help="bandwidth es requerido", default="0")
        ap.add_argument("-hlwu", "--highLevelWarningUplink", required=False, help="highLevelWarningUplink es requerido",
                        default=200)
        ap.add_argument("-hlcu", "--highLevelCriticalUplink", required=False,
                        help="highLevelCriticalUplink es requerido",
                        default=200)
        ap.add_argument("-hlwd", "--highLevelWarningDownlink", required=False,
                        help="highLevelWarningDownlink es requerido",
                        default=200)
        ap.add_argument("-hlcd", "--highLevelCriticalDownlink", required=False,
                        help="highLevelCriticalDownlink es requerido", default=200)
        ap.add_argument("-hlwt", "--highLevelWarningTemperature", required=False,
                        help="highLevelWarningTemperature es requerido", default=200)
        ap.add_argument("-hlct", "--highLevelCriticalTemperature", required=False,
                        help="highLevelCriticalTemperature es requerido", default=200)

        args = vars(ap.parse_args())

        # Check if the high level warning uplink value exists.
        if "highLevelWarningUL" not in args:
            args["highLevelWarningUL"] = 41

        # Check if the high level critical uplink value exists.
        if "highLevelCriticalUL" not in args:
            args["highLevelCriticalUL"] = 38

        # Check if the high level warning downlink value exists.
        if "highLevelWarningDL" not in args:
            args["highLevelWarningDL"] = 41

        # Check if the high level critical downlink value exists.
        if "highLevelCriticalDL" not in args:
            args["highLevelCriticalDL"] = 38

        # Check if the high level warning temperature value exists.
        if "highLevelWarningTemperature" not in args:
            args["highLevelWarningTemperature"] = 50

        # Check if the high level critical temperature value exists.
        if "highLevelCriticalTemperature" not in args:
            args["highLevelCriticalTemperature"] = 45

    except Exception as e:
        # print help information and exit:
        sys.stderr.write("CRITICAL - " + str(e) + "\n")
        cmd_help()
        sys.exit(CRITICAL)

    return args


def create_table(parameters):
    # device_table = dmu_table(parameters) if device == 'dmu' else dru_table(parameters)
    device_table = if_board_table(parameters)
    channel_table = get_channel_freq_table(parameters)
    table = ""
    table += '<div class="sigma-container">'
    table += device_table + channel_table
    table += "</div>"
    return table


def dru_table(parameters):
    power_att_table = get_power_table(parameters)
    vswr_temperature_table = get_vswr_temperature_table(parameters)
    return power_att_table + vswr_temperature_table


def dmu_table(parameters):
    opt_status_table = get_opt_status_table(parameters)
    power_table = get_power_table(parameters)
    return opt_status_table + power_table


def if_board_table(parameters):
    opt_status_table = get_opt_status_table(parameters)
    power_att_table = get_power_table(parameters)
    vswr_temperature_table = get_vswr_temperature_table(parameters)
    return opt_status_table + power_att_table + vswr_temperature_table


def get_channel_table(responseDict):
    if (responseDict['workingMode'] == 'Channel Mode'):
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
            table3 += "<td>" + responseDict["channel" + str(channel) + "Status"] + "</td>"
            table3 += "<td>" + responseDict["channel" + str(channel) + "ulFreq"] + "</td>"
            table3 += "<td>" + responseDict["channel" + str(channel) + "dlFreq"] + "</td>"
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
        table3 += "<td>" + responseDict['workingMode'] + "</td>"

        table3 += "<td>" + responseDict['work_bandwidth'] + "</td>"
        table3 += "<td>" + responseDict['Uplink Start Frequency'] + "</td>"
        table3 += "<td>" + responseDict['Downlink Start Frequency'] + "</td>"

        table3 += "</tr>"

    table3 += "</tbody></table>"
    return table3


def get_power_table(responseDict):
    table2 = "<table width=250>"
    table2 += "<thead>"
    table2 += "<tr  align=\"center\" style=font-size:12px>"
    table2 += "<th width='12%'>Link</font></th>"
    table2 += "<th width='33%'>Power</font> </th>"
    table2 += "<th width='35%'>Attenuation</font></th>"
    table2 += "</tr>"
    table2 += "</thead>"
    table2 += "<tbody>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>Uplink</td><td>" + responseDict[
        'ulInputPower'] + " [dBm]</td><td>" + responseDict['ulAtt'] + " [dB]</td></tr>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>Downlink</td><td>" + responseDict[
        'dlOutputPower'] + " [dBm]</td><td>" + responseDict['dlAtt'] + " [dB]</td></tr>"
    table2 += "</tbody></table>"
    return table2


def get_opt_status_table(responseDict):
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
        connected = str(responseDict[f"{connected_name}{opt}"])
        table1 += "<tr align=\"center\" style=font-size:12px>"
        table1 += "<td>opt" + opt + "</td>"
        table1 += "<td>" + responseDict['opt' + opt + 'ActivationStatus'] + "</td>"
        table1 += "<td>" + connected + "</td>"
        table1 += "<td>" + responseDict['opt' + opt + 'TransmissionStatus'] + "</td>"
        table1 += "</tr>"

    table1 += "</tbody>"
    table1 += "</table>"
    return table1


def get_channel_freq_table(parameter_dic):
    table3 = "<table width=90%>"
    table3 += "<thead><tr style=font-size:11px>"
    table3 += "<th width='10%'>Channel</font></th>"
    table3 += "<th width='10%'>Status</font></th>"
    table3 += "<th width='40%'>UpLink Frequency [Mhz]</font></th>"
    table3 += "<th width='40%'>Downlink Frequency [Mhz]</font></th>"
    table3 += "</tr></thead><tbody>"

    if (parameter_dic['workingMode'] == 'Channel Mode'):
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
            table3 += "<td>" + parameter_dic["channel" + str(channel) + "Status"] + "</td>"
            table3 += "<td>" + parameter_dic["channel_" + str(channel) + "_freq"] + "</td>"
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
        table3 += "<td>" + parameter_dic['workingMode'] + "</td>"
        table3 += "<td>" + str(parameter_dic["work_bandwidth"]) + "</td>"
        # table3 += "<td>" + parameter_dic['Uplink Start Frequency'] + "</td>"
        # table3 += "<td>" + parameter_dic['Downlink Start Frequency'] + "</td>"
        table3 += "<td>" + parameter_dic['central_frequency_point'] + "</td>"

    table3 += "</tbody></table>"
    return table3


def get_vswr_temperature_table(parameter_dic):
    temperature = str(parameter_dic['temperature'])
    table2 = "<table width=90%>"
    table2 += "<thead>"
    table2 += "<tr  style=font-size:12px>"
    table2 += "<th width='40%'>Temperature</font></th>"
    table2 += "<th width='40%'>VSWR</font></th>"
    table2 += "</tr>"
    table2 += "</thead>"
    table2 += "<tbody>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>" + temperature + " [&deg;C]</td><td>" + \
              parameter_dic['vswr'] + "</td></tr>"
    table2 += "</tbody></table>"
    return table2


def blank_parameter(device):
    parameters = {}
    dru_parameters = {'dlOutputPower': '-', 'ulInputPower': '-', 'temperature': '-', 'dlAtt': '-', 'ulAtt': '-',
                      'vswr': '-', 'workingMode': '-', 'mac': '-', 'sn': '-', "Uplink Start Frequency": '-',
                      "Downlink Start Frequency": '-'}

    dmu_parameters = {'optical_port_devices_connected_1': "-", 'optical_port_devices_connected_2': "-",
                      'optical_port_devices_connected_3': "-",
                      'optical_port_devices_connected_4': "-", 'opt1ConnectionStatus': "-", 'opt2ConnectionStatus': "-",
                      'opt3ConnectionStatus': "-", 'opt4ConnectionStatus': "-", 'opt1TransmissionStatus': "-",
                      'opt2TransmissionStatus': "-", 'opt3TransmissionStatus': "-", 'opt4TransmissionStatus': "-",
                      'dlOutputPower': "-", 'ulInputPower': "-", 'ulAtt': "-", 'dlAtt': "-", 'workingMode': "-",
                      'opt1ActivationStatus': '-', 'opt2ActivationStatus': '-', 'opt3ActivationStatus': '-',
                      'opt4ActivationStatus': '-', "Uplink Start Frequency": '-', "Downlink Start Frequency": '-',
                      'temperature': '-', 'central_frequency_point': '-'}

    channel_parameters = blank_channel_dict()

    parameters.update(dru_parameters)
    parameters.update(dmu_parameters)
    parameters.update(channel_parameters)
    return parameters


def blank_parameter_old(device):
    if device == 'dru':
        parameters = {'dlOutputPower': '-', 'ulInputPower': '-', 'temperature': '-', 'dlAtt': '-', 'ulAtt': '-',
                      'vswr': '-', 'workingMode': '-', 'mac': '-', 'sn': '-', "Uplink Start Frequency": '-',
                      "Downlink Start Frequency": '-', "work_bandwidth": '-'}
        blank_channel_dict_old(parameters)
        return parameters

    elif device == 'dmu':
        parameters = {'optical_port_devices_connected_1': "-", 'optical_port_devices_connected_2': "-",
                      'optical_port_devices_connected_3': "-",
                      'optical_port_devices_connected_4': "-", 'opt1ConnectionStatus': "-", 'opt2ConnectionStatus': "-",
                      'opt3ConnectionStatus': "-", 'opt4ConnectionStatus': "-", 'opt1TransmissionStatus': "-",
                      'opt2TransmissionStatus': "-", 'opt3TransmissionStatus': "-", 'opt4TransmissionStatus': "-",
                      'dlOutputPower': "-", 'ulInputPower': "-", 'ulAtt': "-", 'dlAtt': "-", 'workingMode': "-",
                      'opt1ActivationStatus': '-', 'opt2ActivationStatus': '-', 'opt3ActivationStatus': '-',
                      'opt4ActivationStatus': '-', "Uplink Start Frequency": '-', "Downlink Start Frequency": '-',
                      'work_bandwidth': '-', 'temperature': '-', 'central_frequency_point': '-'}
        blank_channel_dict_old(parameters)
        return parameters
    return {}


def blank_channel_dict_old(parameters):
    channel = 1
    while channel <= 16:
        parameters["channel" + str(channel) + "Status"] = "-"
        parameters["channel" + str(channel) + "ulFreq"] = "-"
        parameters["channel" + str(channel) + "dlFreq"] = "-"
        parameters["channel_" + str(channel) + "_freq"] = "-"
        channel += 1


def blank_channel_dict():
    parameters = {}
    channel = 1
    while channel <= 16:
        parameters["channel" + str(channel) + "Status"] = "-"
        parameters["channel" + str(channel) + "ulFreq"] = "-"
        parameters["channel" + str(channel) + "dlFreq"] = "-"
        parameters["channel_" + str(channel) + "_freq"] = "-"
        channel += 1
    return parameters


def get_graphite(parameters):
    hl_warning_uplink = parameters['highLevelWarningUL']
    hl_critical_uplink = parameters['highLevelCriticalUL']
    hl_warning_downlink = parameters['highLevelWarningDL']
    hl_critical_downlink = parameters['highLevelCriticalDL']
    hl_warning_temperature = parameters['highLevelWarningTemperature']
    hl_critical_temperature = parameters['highLevelCriticalTemperature']
    downlink_power = parameters['dlOutputPower']
    uplink_power = parameters['ulInputPower']
    temperature = parameters['temperature']

    graphite = ""

    if parameters['device'] == 'dmu':
        dl_str = f"Downlink={downlink_power}"
        dl_str += ";" + str(hl_warning_downlink)
        dl_str += ";" + str(hl_critical_downlink)
        rt_str = "RT=" + parameters['rt'] + ";1000;2000"
        graphite = rt_str + " " + dl_str

    elif parameters['device'] == 'dru':
        if downlink_power == 0.0:
            downlink_power = "-"
        else:
            downlink_power = str(downlink_power)
        pa_temperature = "Temperature=" + str(parameters['temperature'])
        pa_temperature += ";" + str(hl_warning_temperature)
        pa_temperature += ";" + str(hl_critical_temperature)
        dl_str = f"Downlink={downlink_power}"
        dl_str += ";" + str(hl_warning_downlink)
        dl_str += ";" + str(hl_critical_downlink)
        vswr = "VSWR=" + parameters['vswr']
        up_str = f"Uplink={uplink_power}"
        up_str += ";" + str(hl_warning_uplink)
        up_str += ";" + str(hl_critical_uplink)
        rt = "RT=" + parameters['rt'] + ";1000;2000"

        graphite = rt + " " + pa_temperature + " " + dl_str + " " + vswr + " " + up_str
    return graphite


def display_alarm(parameters):
    hl_warning_uplink = parameters['highLevelWarningUL']
    hl_critical_uplink = parameters['highLevelCriticalUL']
    hl_warning_downlink = parameters['highLevelWarningDL']
    hl_critical_downlink = parameters['highLevelCriticalDL']
    hl_warning_temperature = parameters['highLevelWarningTemperature']
    hl_critical_temperature = parameters['highLevelCriticalTemperature']

    if parameters['dlOutputPower'] != '-':
        dlPower = float(parameters['dlOutputPower'])
    else:
        dlPower = -200
    if parameters['ulInputPower'] != '-':
        ulPower = float(parameters['ulInputPower'])
    else:
        ulPower = -200
    if parameters['temperature'] != '-':
        temperature = float(parameters['temperature'])
    else:
        temperature = -200

    alarm = ""

    if dlPower >= hl_critical_downlink:
        alarm += "<h3><font color=\"#ff5566\">Downlink Power Level Critical "
        alarm += parameters['dlOutputPower']
        alarm += " [dBn]!</font></h3>"

    elif dlPower >= hl_warning_downlink:
        alarm += "<h3><font color=\"#ffaa44\">Downlink Power Level Warning "
        alarm += parameters['dlOutputPower']
        alarm += "[dBm]</font></h3>"

    if ulPower >= hl_critical_uplink:
        alarm += "<h3><font color=\"#ff5566\">Uplink Power Level Critical "
        alarm += parameters['ulInputPower']
        alarm += "[dBm]!</font></h3>"

    elif ulPower >= hl_warning_uplink:
        alarm += "<h3><font color=\"#ffaa44\">Uplink Power Level Warning "
        alarm += parameters['ulInputPower']
        alarm += "[dBm]</font></h3>"

    if temperature >= hl_critical_temperature:
        alarm += "<h3><font color=\"#ff5566\">Temperature Level Critical "
        alarm += parameters['temperature']
        alarm += " [&deg;C]]!</font></h3>"

    elif temperature >= hl_warning_temperature:
        alarm += "<h3><font color=\"#ffaa44\">Temperature Level Warning "
        alarm += parameters['temperature']
        alarm += " [&deg;C]]!</font></h3>"

    return alarm


def query_cmd_list(query_command_numnber):
    cmd_list = []
    for cmd_name in query_command_numnber:
        cmd_data = CommandData(
            module_address=0,
            module_link=DONWLINK_MODULE,
            module_function=0x07,
            command_type=DataType.DATA_INITIATION,
            command_number=cmd_name,
            command_body_length=0x00,
            command_data=0x00,
            response_flag=ResponseFlag.SUCCESS
        )
        if cmd_data.query != "":
            cmd_list.append(cmd_data)

    return cmd_list


def reply_decode(cmd_list, device):
    parameters = blank_parameter(device)
    for cmd_name in cmd_list:
        #            print(cmd_name)
        cmd_name.extract_data()
        message = Queries.decode(cmd_name.command_number, cmd_name.reply_command_data)
        if len(message) != 0:
            parameters.update(message)

            #        print(message)
    return parameters


def transmit_and_receive(address, cmd_list, target_port):
    for cmd_name in cmd_list:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((address, target_port))
                sock.settimeout(1)
                data_bytes = bytearray.fromhex(cmd_name.query)
                sock.sendall(data_bytes)
                data_received = sock.recv(1024)
                sock.close()
                cmd_name.reply = data_received
        except Exception as e:
            sys.stderr.write("CRITICAL - " + str(e))
            sys.exit(CRITICAL)


def discovery(parameters):
    opt = parameters['port']
    hostname = parameters['hostname']
    net = parameters["device_id"]
    dru_connected = {}
    fix_ip_end_opt = [0, 100, 120, 140, 160]  # You can adjust these values according to your logic
    port_name = f"optical_port_devices_connected_{opt}"
    optical_port_connected_ip_addr = {}
    dru_connected[f"opt{opt}"] = []
    last_connected = parameters[port_name]
    for connected in range(1, parameters[port_name] + 1):
        connected_ip_addr_name = f"optical_port_connected_ip_addr_{opt}{connected}"
        id_key = f"optical_port_device_id_topology_{opt}"
        device_id = parameters[id_key][f"id_{connected}"]
        # if connected == last_connected and last_connected > 1 and False:
        #    parent = [hostname, dru_connected[f"opt{opt}"][connected - 2].hostname]
        # else:
        parent = hostname if connected == 1 else dru_connected[f"opt{opt}"][connected - 2].hostname
        ip = f"{fix_ip_start}.{net}.{fix_ip_end_opt[opt] + connected - 1}"  # You can use a list to store the different values of fix_ip_end_opt
        # sys.stderr.write(ip + "\n")
        if device_id != 0:
            d = DRU(connected, opt, device_id, hostname, ip, parent)
            dru_connected[f"opt{opt}"].append(d)
            parameters[connected_ip_addr_name] = ip
            # sys.stderr.write(connected_ip_addr_name + ": " + ip + "\n")
            # sys.stderr.write(str(d) + "\n")
    hostname = socket.gethostname()
    master_host = socket.gethostbyname(hostname)
    director = Director(master_host)
    deploy = 0
    for opt in dru_connected:
        for dru in dru_connected[opt]:
            response = director.create_dru_host(dru)
            sys.stderr.write(f"{dru} {response.status_code} \n")
            if response.status_code != 304:
                director.deploy()


def discovery_plugin_output(parameters):
    rt = parameters['rt']
    dt = parameters['dt']
    rt_str = "RT=" + rt
    rt_str += ";" + str(1)
    rt_str += ";" + str(1)
    dt_str = "DT=" + dt
    dt_str += ";" + str(2)
    dt_str += ";" + str(2)
    graphite = rt_str + " " + dt_str
    sys.stderr.write("\nSummary - " + "discovery_str")
    sys.stderr.write("|" + graphite)
    sys.exit(OK)


def update_parameters_with_args(args, parameters):
    parameters['address'] = args['address']
    parameters['device'] = args['device']
    parameters['hostname'] = args['hostname']
    parameters['port'] = int(args['port'])
    parameters['work_bandwidth'] = int(args['bandwidth'])
    parameters['highLevelWarningUL'] = int(args['highLevelWarningUL'])
    parameters['highLevelCriticalUL'] = int(args['highLevelCriticalUL'])
    parameters['highLevelWarningDL'] = int(args['highLevelWarningDL'])
    parameters['highLevelCriticalDL'] = int(args['highLevelCriticalDL'])
    parameters['highLevelWarningTemperature'] = int(args['highLevelWarningTemperature'])
    parameters['highLevelCriticalTemperature'] = int(args['highLevelCriticalTemperature'])


def device_host_plugin_ouput(parameters):
    downlink_power = float(parameters['dlOutputPower']) if parameters['dlOutputPower'] != "-" else 100.0
    uplink_power = float(parameters['ulInputPower']) if parameters['ulInputPower'] != "-" else 100.0
    temperature = parameters['temperature']

    graphite = ""
    if downlink_power > 50.0:
        parameters['dlOutputPower'] = "-"
    if uplink_power > 50.0:
        parameters['ulInputPower'] = "-"

    alarm = display_alarm(parameters)
    parameter_html_table = create_table(parameters)
    graphite = get_graphite(parameters)
    sys.stderr.write(alarm + parameter_html_table + "|" + graphite)
    if alarm != "":
        sys.exit(1)
    else:
        sys.exit(0)


def get_cmd_name_query(device):
    if device == 'dmu':
        query_cmd_name_query = DRSMasterCommand
    elif device == 'dru':
        query_cmd_name_query = DRSRemoteCommand
    elif device == 'discovery':
        query_cmd_name_query = DiscoveryCommand
    else:
        sys.stderr.write("CRITICAL - no device")
        sys.exit(CRITICAL)
    return query_cmd_name_query


def get_setting_command_value(int_number):
    for command in SettingCommand:
        if command.value == int_number:
            return command
    return None


# ----------------------
#   MAIN
# ----------------------
def main():
    # -- Analizar los argumentos pasados por el usuario
    args = args_check()
    address = args['address']
    device = args['device']
    hostname = args['hostname']
    port = int(args['port'])
    cmd_name = int(args['cmd_name'])
    cmd_body_length = int(args['cmd_body_length'])
    cmd_data = int(args['cmd_data'])
    type = int(args['type'])

    if type == SET:
        cmd_name = get_setting_command_value(cmd_name)
        cmd_data = CommandData(
            module_address=0,
            module_link=DONWLINK_MODULE,
            module_function=0x07,
            command_type=DataType.DATA_INITIATION,
            command_number=cmd_name,
            command_body_length=cmd_body_length,
            command_data=cmd_data,
            response_flag=ResponseFlag.SUCCESS
        )
        cmd_list = list()
        cmd_list.append(cmd_data)
    else:
        cmd_name_query = get_cmd_name_query(device)
        cmd_list = query_cmd_list(cmd_name_query)
    start_time = time.time()
    if_board_query_port = 65050  # Replace with the actual port number
    remote_external_device_query_port = 65053  # Replace with the actual port number
    transmit_and_receive(address, cmd_list, if_board_query_port)
    parameters = reply_decode(cmd_list, device)
    parameters["rt"] = str(time.time() - start_time)
    start_time = time.time()
    update_parameters_with_args(args, parameters)
    if device == "dru" or device == "dmu":
        device_host_plugin_ouput(parameters)
    elif 0 < port < 5:
        discovery(parameters)
        parameters["dt"] = str(time.time() - start_time)
        discovery_plugin_output(parameters)
    else:
        sys.stderr.write("\nOK - " + "no command")
        sys.exit(OK)


if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN
