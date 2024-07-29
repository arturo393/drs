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
# import dru_discovery as discovery
import time
import socket
import json
import requests
import serial
import struct
import os
from enum import IntEnum, Enum
from typing import Optional
from typing import Tuple

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# Define constant values
DEFAULT_WARNING_UPLINK_THRESHOLD = 200
DEFAULT_CRITICAL_UPLINK_THRESHOLD = 200
DEFAULT_WARNING_DOWNLINK_THRESHOLD = 200
DEFAULT_CRITICAL_DOWNLINK_THRESHOLD = 200
DEFAULT_WARNING_TEMPERATURE_THRESHOLD = 200
DEFAULT_CRITICAL_TEMPERATURE_THRESHOLD = 200

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
#    datt = HardwarePeripheralDeviceParameterCommand.datt


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
    #rx0_iir_bandwidth = Rx0QueryCmd.rx0_iir_bandwidth


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


class DiscoveryRedBoardCommand(IntEnum):
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


class CommBoardCmd(Enum):
    channel_switch_bit = (0x05, 0x160A)
    channel_1_number = (0x05, 0x1004)
    channel_2_number = (0x05, 0x1104)
    channel_3_number = (0x05, 0x1204)
    channel_4_number = (0x05, 0x1304)
    channel_5_number = (0x05, 0x1404)
    channel_6_number = (0x05, 0x1504)
    channel_7_number = (0x05, 0x1604)
    channel_8_number = (0x05, 0x1704)
    channel_9_number = (0x05, 0x1804)
    channel_10_number = (0x05, 0x1904)
    channel_11_number = (0x05, 0x1a04)
    channel_12_number = (0x05, 0x1b04)
    channel_13_number = (0x05, 0x1c04)
    channel_14_number = (0x05, 0x1d04)
    channel_15_number = (0x05, 0x1e04)
    channel_16_number = (0x05, 0x1f04)
    uplink_att = (0x04, 0x4004)
    downlink_att = (0x04, 0x4104)
    working_mode = (0x04, 0xEF0B)
    downlink_vswr = (0x04, 0x0605)
    downlink_output_power = (0x04, 0x0305)
    uplink_input_power = (0x04, 0x2505)
    power_amplifier_temperature = (0x04, 0x0105)
    uplink_start_frequency = (0x07, 0x180A)
    downlink_start_frequency = (0x07, 0x190A)
    work_bandwidth = (0x07, 0x1A0A)
    channel_bandwidth = (0x07, 0x1B0A)


class ChannelCommBoardCmd(Enum):
    channel_switch_bit = (0x05, 0x160A)
    channel_1_number = (0x05, 0x1004)
    channel_2_number = (0x05, 0x1104)
    channel_3_number = (0x05, 0x1204)
    channel_4_number = (0x05, 0x1304)
    channel_5_number = (0x05, 0x1404)
    channel_6_number = (0x05, 0x1504)
    channel_7_number = (0x05, 0x1604)
    channel_8_number = (0x05, 0x1704)
    channel_9_number = (0x05, 0x1804)
    channel_10_number = (0x05, 0x1904)
    channel_11_number = (0x05, 0x1a04)
    channel_12_number = (0x05, 0x1b04)
    channel_13_number = (0x05, 0x1c04)
    channel_14_number = (0x05, 0x1d04)
    channel_15_number = (0x05, 0x1e04)
    channel_16_number = (0x05, 0x1f04)


class FreqCommBoardCmd(Enum):
    uplink_start_frequency = (0x07, 0x180A)
    # downlink_start_frequency = (0x07, 0x190A)
    work_bandwidth = (0x07, 0x1A0A)
    channel_bandwidth = (0x07, 0x1B0A)


class ParametersCommBoardCmd(Enum):
    # rf_power_sitch = (0x04,0x0104)
    uplink_att = (0x04, 0x4004)
    downlink_att = (0x04, 0x4104)
    working_mode = (0x04, 0xEF0B)
    downlink_vswr = (0x04, 0x0605)
    downlink_output_power = (0x04, 0x0305)
    uplink_input_power = (0x04, 0x2505)
    power_amplifier_temperature = (0x04, 0x0105)


class CommBoardGroupCmd(Enum):
    channel = ''.join([f"{cmd.value[0]:02X}{cmd.value[1]:04X}0000" for cmd in ChannelCommBoardCmd])
    parameters = ''.join([f"{cmd.value[0]:02X}{cmd.value[1]:04X}00" for cmd in ParametersCommBoardCmd])
    frequencies = ''.join([f"{cmd.value[0]:02X}{cmd.value[1]:04X}00000000" for cmd in FreqCommBoardCmd])


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
        return self.position == other.position and self.port == other.position


class Icinga_Api:
    icinga_api_login = "root"
    icinga_api_password = "Admin.123"

    def __init__(self, master_host):
        self.master_host = master_host

    def _modify_hostname_service(self, hostname, servicename, icinga_query: {}):

        request_url = f"https://{self.master_host}:5665/v1/objects/hosts/{hostname}"
        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(icinga_query),
                              auth=(self.icinga_api_login, self.icinga_api_password),
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

    def _log_status(self, message):
        """
        Log status messages to stderr.

        Args:
            message (str): The status message to log.
        """

        sys.stderr.write(f"{message} \n")

    def _process_dmu_response(self, message, response):
        """
        Process and log the response from Icinga 2 Director, and deploy changes if necessary.

        Args:
            message (str): The status message to log.
            response (requests.Response): The response from the API call.
        """
        if response.status_code != 304:
            self._log_status(message)


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

    def get_dru_name(self, dru: DRU):

        # Construct query parameters as a string
        query_params = f"name={dru.hostname}"

        request_url = f"http://{self.master_host}/director/host?{query_params}"
        headers = {'Accept': 'application/json'}  # Remove unnecessary header

        try:
            q = requests.get(request_url,
                             headers=headers,
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


class Command:
    list = list()
    tcp_port = 65050
    master_to_rs485_udp_port = 65055
    remote_to_rs485_udp_port = 65053

    def __init__(self, args):

        self.cmd_number_ok = None
        self.serial = None
        self.parameters = {}
        self.set_args(args)
        self.message_type = None

    def set_args(self, args):
        self.parameters['address'] = args['address']
        self.parameters['device'] = args['device']
        self.parameters['hostname'] = args['hostname']
        self.parameters['cmd_type'] = args['cmd_type']
        self.parameters['cmd_data'] = args['cmd_data']

        if isinstance(args['cmd_name'], str):
            if len(args['cmd_name']) < 4:
                self.parameters['cmd_name'] = int(args['cmd_name'])
            if len(args['cmd_name']) == 4:
                self.parameters['cmd_name'] = int(args['cmd_name'], 16)

        self.parameters['cmd_body_length'] = int(args['cmd_body_length'])
        self.parameters['device_number'] = int(args['device_number'])
        self.parameters['optical_port'] = int(args['optical_port'])
        self.parameters['work_bandwidth'] = int(args['bandwidth'])
        self.parameters['warning_uplink_threshold'] = int(args['warning_uplink_threshold'])
        self.parameters['critical_uplink_threshold'] = int(args['critical_uplink_threshold'])
        self.parameters['warning_downlink_threshold'] = int(args['warning_downlink_threshold'])
        self.parameters['critical_downlink_threshold'] = int(args['critical_downlink_threshold'])
        self.parameters['warning_temperature_threshold'] = int(args['warning_temperature_threshold'])
        self.parameters['critical_temperature_threshold'] = int(args['critical_temperature_threshold'])

        opt, dru = self._decode_address(self.parameters['address'])
        self.parameters['device_number'] = dru
        self.parameters['optical_port'] = opt
        self.parameters['baud_rate'] = int(args['baud_rate'])

    def create_command(self, cmd_type):
        """Create command based on type.

        Args: 
            cmd_type (str): Type of command to create
        
        Returns:
            (int, str): Tuple with status code and message
        """

        if cmd_type == "single_set":
            is_created = self._create_single_command()
        elif cmd_type == "single_query":
            is_created = self._create_single_command()
        elif cmd_type == "group_query":
            is_created = self._create_group_query_command()
        else:
            return CRITICAL, f"No command type {cmd_type} defined"

        if is_created:
            return OK, f"Created {is_created} {cmd_type} commands"
        else:
            return CRITICAL, f"No {cmd_type} commands created"

    def _create_single_command(self):
        """Generates a single command frame.

        Returns:
            int: The length of the command frame, in bytes.
        """
        cmd_data = CommandData()

        dru = self.parameters['device_number']
        opt = self.parameters['optical_port']
        frame_len = 0
        if self.parameters['cmd_name'] > 255:
            cmd_data.generate_ltel_comunication_board_frame(
                dru_id=f"{dru}{opt}",
                cmd_name=self.get_command_comm_board_value(),
                message_type=0x03
            )
            self.message_type = 0x03
            frame_len = 1
        else:
            frame_len = cmd_data.generate_ifboard_frame(
                command_number=self.get_command_value(),
                command_body_length=self.parameters['cmd_body_length'],
                command_data=self.parameters['cmd_data'],
            )

        if frame_len > 0:
            self.list.append(cmd_data)

        return frame_len if frame_len > 0 else -2

    def _decode_address(self, address: str) -> Optional[Tuple[int, int]]:
        """
        Decodes the address string provided in the configuration and returns a tuple of (opt, dru) values.

        Args:
            address (str): The address string to decode.

        Returns:
            Optional[Tuple[int, int]]: A tuple containing the decoded opt and dru values, or None if the address format is invalid.
        """

        if not address.startswith("192.168.11"):
            sys.stderr.write(f"UNKNOWN - Invalid start address format: {address}")
            sys.exit(UNKNOWN)

        if address == "192.168.11.22":
            return 0, 0

        try:
            # Determine the opt value based on the starting byte of the IP address
            opt = 0
            if address.startswith("192.168.11.10"):
                opt = 1
            elif address.startswith("192.168.11.12"):
                opt = 2
            elif address.startswith("192.168.11.14"):
                opt = 3
            elif address.startswith("192.168.11.16"):
                opt = 4

            # Extract the dru number from the last byte of the IP address
            dru = int(address.strip()[-1:]) + 1

            return opt, dru
        except (IndexError, KeyError, ValueError):
            sys.stderr.write(f"UNKNOWN - Invalid address format: {address}")
            sys.exit(UNKNOWN)

    def _create_group_query_command(self):
        """Creates a group query for the given device.

        Returns:
            int: The number of commands in the group query.
        """

        cmd_name_map = dict(
            dmu_ethernet=DRSMasterCommand,
            dru_ethernet=DRSRemoteCommand,
            discovery_ethernet=DiscoveryCommand,
            discovery_serial=DiscoveryCommand,
            dmu_serial_service=DRSMasterCommand,
            dru_serial_service=CommBoardGroupCmd,
            discovery_redboard_serial=DiscoveryRedBoardCommand
        )

        device = self.parameters['device']
        if device in cmd_name_map:
            cmd_group = cmd_name_map[device]
            if cmd_group == CommBoardCmd:
                opt = self.parameters['optical_port']
                dru = self.parameters['device_number']
                dru_id = f"{opt}{dru}"
                for cmd_name in cmd_group:
                    cmd_data = CommandData()
                    cmd_data.generate_ltel_comunication_board_frame(dru_id=dru_id, cmd_name=cmd_name, message_type=0x02)
                    if cmd_data.query != "":
                        self.list.append(cmd_data)

            elif cmd_group == CommBoardGroupCmd:
                opt = self.parameters['optical_port']
                dru = self.parameters['device_number']
                dru_id = f"{opt}{dru}"
                for cmd in cmd_group:
                    cmd_data = CommandData()
                    cmd_data.generate_comm_board_group_frame(dru_id=dru_id, cmd_name_group=cmd)
                    self.list.append(cmd_data)
            else:
                for cmd_name in cmd_group:
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
            self._exit_messagge(UNKNOWN, message=f"No commands created")

    def _exit_messagge(self, code, message):
        if code == CRITICAL:
            sys.stderr.write(f"CRITICAL - {message}")
        elif code == WARNING:
            sys.stderr.write(f"WARNING - {message}")
        else:
            sys.stderr.write(f"UNKNOWN - {message}")

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

    def get_command_comm_board_value(self):
        int_number = self.parameters['cmd_name']

        for command in CommBoardCmd:
            if command.value[1] == int_number:
                return command
        return None

    def _transmit_and_receive_tcp(self, address):
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

    def _transmit_and_receive_serial_comm_board(self, port, baud):
        """
        Transmits and receives serial data.

        Args:
            port (str): The name of the serial port.
            baud (int): The baud rate of the serial connection.

        Raises:
            ValueError: If the port is not available.

        Returns:
            int: The number of successful commands.
        """
        if self.message_type == 0x03:
            timeout = 10
        else:
            timeout = 6
        try:
            rt = time.time()
            self.serial = self.set_serial_with_timeout(port, baud, timeout=timeout)
        except serial.SerialException:
            sys.stderr.write(f"CRITICAL - The specified port {port} is not available at {baud}")
            sys.exit(CRITICAL)

        self.cmd_number_ok = 0

        for cmd_name in self.list:
            cmd_name.query_bytes = bytearray.fromhex(cmd_name.query)
            self.serial.write(cmd_name.query_bytes)
            self.serial.flush()
            cmd_name.reply_bytes = b''
            retry = 0
            while True:
                cmd_name.reply_bytes = self.serial.read(200)
                cmd_name.reply = cmd_name.reply_bytes.hex()
                if self._isValidReply(cmd_name) is True:
                    self.cmd_number_ok += 1
                    break
                self.serial.write(cmd_name.query_bytes)
                retry += 1
                if retry == 3:
                    break
        self.serial.close()
        rt = time.time() - rt
        self.parameters['rt'] = rt
        return self.cmd_number_ok

    def _isValidReply(self, cmd_name):
        start_index = 0
        id_index = 7
        cmd_code_index = 15
        if cmd_name.reply_bytes == b'':
            return False
        if len(cmd_name.query_bytes) != len(cmd_name.reply_bytes):
            return False
        if cmd_name.query_bytes[start_index] != cmd_name.reply_bytes[start_index]:
            return False
        if cmd_name.query_bytes[id_index] != cmd_name.reply_bytes[id_index]:
            return False
        if cmd_name.query_bytes[cmd_code_index] != cmd_name.reply_bytes[cmd_code_index]:
            return False
        if cmd_name.query_bytes[cmd_code_index + 1] != cmd_name.reply_bytes[cmd_code_index + 1]:
            return False
        return True

    def _transmit_and_receive_serial(self, port, baud):
        """
        Transmits and receives serial data.

        Args:
            port (str): The name of the serial port.
            baud (int): The baud rate of the serial connection.

        Raises:
            ValueError: If the port is not available.

        Returns:
            int: The number of successful commands.
        """
        try:
            rt = time.time()
            self.serial = self.setSerial(port, baud)
        except serial.SerialException:
            sys.stderr.write(f"CRITICAL - The specified port {port} is not available at {baud}")
            sys.exit(CRITICAL)

        self.cmd_number_ok = 0
        for cmd_name in self.list:

            self.write_serial_frame(cmd_name.query)
            query_time = time.time()
            data_received = self.read_serial_frame()
            cmd_name.reply = data_received
            if cmd_name.reply != "":
                self.cmd_number_ok += 1
            tmp = time.time() - query_time
            time.sleep(tmp)

        self.serial.close()
        rt = str(time.time() - rt)
        self.parameters['rt'] = rt
        return self.cmd_number_ok

    def write_serial_frame(self, Trama):
        """
        Writes a serial frame to the serial port.

        Args:
            Trama (str): The serial frame in hexadecimal format.

        Raises:
            ValueError: If the frame is not in hexadecimal format.

        Returns:
            None
        """
        try:
            cmd_bytes = bytearray.fromhex(Trama)
        except ValueError:
            sys.stderr.write(f"CRITICAL - Invalid hexadecimal format for the frame {Trama}")
            sys.exit(CRITICAL)

        hex_byte = ''
        for cmd_byte in cmd_bytes:
            hex_byte = "{0:02x}".format(cmd_byte)
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

            if command.command_number in CommBoardCmd:
                decoded_commands += self._decode_ltel_command(command)
            elif command.command_number in CommBoardGroupCmd:
                decoded_commands += self._decode_comm_board_command(command)
            else:
                decoded_commands += self._decode_ifboard_command(command)

            # Update the parameters with the decoded data.
            if command.message:
                self.parameters.update(command.message)

        return decoded_commands

    def _decode_ifboard_command(self, command: CommandData) -> int:
        reply_len = len(command.reply)
        query_len = len(command.query)
        if self.parameters['cmd_type'] == 'group_query':
            if len(command.reply) < len(command.query) / 2:
                return 0

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

    def _decode_comm_board_command(self, command):
        """
        Decodes a LtelDru command and handles the processing of command data.

        Args:
            command (CommandData): The command to decode.

        Returns:
            int: The number of decoded commands.
        """
        try:
            if not command.reply:
                return 0
            respond_flag_index = 10
            cmd_data_start_index = 14
            cmd_data_end_index = len(command.reply_bytes) - 4
            try:
                response_flag = command.reply_bytes[respond_flag_index]
                command_body = command.reply_bytes[cmd_data_start_index:cmd_data_end_index]
                command_body_str = command_body.hex()
            except IndexError as e:
                sys.stderr.write(f"UNKNOWN - command.reply is too short for {command.command_number}: {e}")
                sys.exit(UNKNOWN)

            if response_flag == ResponseFlag.SUCCESS:
                command.reply_command_data = command_body
                try:
                    command.message = Decoder.comm_board_decode(command.command_number,
                                                                command_body)
                except (TypeError, ValueError) as e:
                    sys.stderr.write(f"UNKNOWN - Cannot decode command number: {e}")
                    sys.exit(UNKNOWN)
                return 1
            else:
                return 0

        except Exception as e:
            sys.stderr.write(f"UNKNOWN - An error occurred during command decoding: {e}")
            sys.exit(UNKNOWN)

    def _decode_ltel_command(self, command: CommandData) -> int:
        """
        Decodes a LtelDru command and handles the processing of command data.

        Args:
            command (CommandData): The command to decode.

        Returns:
            int: The number of decoded commands.
        """
        try:
            # Check if command.reply is empty; return 0 if so
            if not command.reply_bytes:
                return 0

            # Define necessary indices
            respond_flag_index = 10
            cmd_body_length_index = 14
            cmd_data_index = 17

            # Extract response flag, command body length, and command body
            # Catch IndexError if command.reply is shorter than expected
            try:
                response_flag = command.reply_bytes[respond_flag_index]
                command_body_length = command.reply_bytes[cmd_body_length_index] - 3
                command_body = command.reply_bytes[cmd_data_index: \
                                                   cmd_data_index + command_body_length]
            except IndexError as e:
                sys.stderr.write(f"UNKNOWN - command.reply is too short for {command.command_number}: {e}")
                sys.exit(UNKNOWN)

            # Check if response flag indicates success
            if response_flag == ResponseFlag.SUCCESS:
                command.reply_command_data = command_body
                # Attempt to decode command number
                try:
                    command.message = Decoder.ltel_decode(command.command_number,
                                                          command_body)
                except (TypeError, ValueError) as e:
                    sys.stderr.write(f"UNKNOWN - Cannot decode command number: {e}")
                    sys.exit(UNKNOWN)
                return 1
            else:
                return 0

        except Exception as e:
            sys.stderr.write(f"UNKNOWN - An error occurred during command decoding: {e}")
            sys.exit(UNKNOWN)

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

    def set_serial_with_timeout(self, port, baudrate, timeout):
        for times in range(3):
            try:
                s = serial.Serial(port, baudrate)
                s.timeout = timeout
                s.exclusive = True
                return s

            except serial.SerialException as e:
                time.sleep(1)
                if times == 2:
                    sys.stderr.write("CRITICAL - " + (e.args.__str__()) + str(port))
                    sys.exit(CRITICAL)

    def transmit_and_receive(self):
        """
        Transmit and receive data based on device and address.
        """
        try:
            device = self.parameters.get('device')
            address = self.parameters.get('address')
            baud_rate = self.parameters.get('baud_rate')

            os_name = os.name.lower()
            port_dmu, port_dru = self._get_ports(os_name)

            if device in ['dmu_serial_host', 'dmu_serial_service', 'dru_serial_host', 'discovery_serial',
                          'discovery_redboard_serial']:
                if not self._transmit_and_receive_serial(baud=baud_rate, port=port_dmu):
                    return CRITICAL, self._print_error(port_dmu)

            elif device == 'dru_serial_service':
                if not self._transmit_and_receive_serial_comm_board(baud=baud_rate, port=port_dru):
                    return CRITICAL, self._print_error(port_dru)

            else:
                if not self._transmit_and_receive_tcp(address):
                    return CRITICAL, self._print_error(address)

            return OK, f"received data"
        except Exception as e:
            return CRITICAL, f"Error: {e}"

    def _get_ports(self, os_name):
        """Get serial port names based on OS."""
        if os_name == 'posix':
            return '/dev/ttyS0', '/dev/ttyS1'
        elif os_name == 'nt':
            return 'COM2', 'COM3'
        else:
            sys.stderr.write("OS not recognized, using default action.")
            return '', ''

    def _print_error(self, device):
        """Print error message."""
        return (f"no response from {device}")

    def _exit_messagge(self, code, message):
        if code == CRITICAL:
            sys.stderr.write(f"CRITICAL - {message}")
        elif code == WARNING:
            sys.stderr.write(f"WARNING - {message}")
        else:
            sys.stderr.write(f"UNKNOWN - {message}")


class Alarm:
    """
    Class to manage alarm conditions and generate HTML output.
    """

    def __init__(self, parameters):
        """
        Initialize the alarm object with the provided parameters.

        Args:
            parameters (dict): A dictionary containing alarm parameters.
        """
        self.parameters = parameters

        self.uplink_power_alarm = OK
        self.downlink_power_alarm = OK
        self.temperature_alarm = OK

        # Extract alarm thresholds from parameters with default values
        self.critical_uplink_power_threshold = self.parameters.get('critical_uplink_threshold',
                                                                   DEFAULT_CRITICAL_UPLINK_THRESHOLD)
        self.warning_uplink_power_threshold = self.parameters.get('warning_uplink_threshold',
                                                                  DEFAULT_WARNING_UPLINK_THRESHOLD)
        self.critical_downlink_power_threshold = self.parameters.get('critical_downlink_threshold',
                                                                     DEFAULT_CRITICAL_DOWNLINK_THRESHOLD)
        self.warning_downlink_power_threshold = self.parameters.get('warning_downlink_threshold',
                                                                    DEFAULT_WARNING_DOWNLINK_THRESHOLD)
        self.critical_temperature_threshold = self.parameters.get('critical_temperature_threshold',
                                                                  DEFAULT_CRITICAL_TEMPERATURE_THRESHOLD)
        self.warning_temperature_threshold = self.parameters.get('warning_temperature_threshold',
                                                                 DEFAULT_WARNING_TEMPERATURE_THRESHOLD)

        self.check_alarm()

    def check_exit_code(self):

        if self.uplink_power_alarm == CRITICAL or self.downlink_power_alarm == CRITICAL or self.temperature_alarm == CRITICAL:
            return CRITICAL
        elif self.uplink_power_alarm == WARNING or self.downlink_power_alarm == WARNING or self.temperature_alarm == WARNING:
            return WARNING

    def check_alarm(self):
        """
        Check for alarm conditions and update alarm properties accordingly.

        Returns:
            str: Alarm message if any alarm condition is detected, empty string otherwise.
        """

        # Extract power and temperature values from parameters
        downlink_power = self.parameters.get('downlink_output_power', -200)
        uplink_power = self.parameters.get('uplink_input_power', -200)
        temperature = self.parameters.get('temperature', -200)

        alarm = ""

        # Check downlink power alarm conditions and update color/font size if necessary
        self._update_color_and_font_size(downlink_power, 'downlink_power')

        # Check uplink power alarm conditions and update color/font size if necessary
        self._update_color_and_font_size(uplink_power, 'uplink_power')

        # Check temperature alarm conditions and update color/font size if necessary
        self._update_color_and_font_size(temperature, 'temperature')

    def _get_value(self, parameter_value, default_value):
        """
        Retrieve the value of a parameter, using the default value if the parameter is not found or is '-'.

        Args:
            parameter_value (str): The value of the parameter from the input data.
            default_value (float): The default value to use if the parameter is not found or is '-'.

        Returns:
            float: The actual value of the parameter or the default value.
        """
        if parameter_value != '-':
            return float(parameter_value)
        else:
            return default_value

    def _update_color_and_font_size(self, value, parameter_name):
        """
        Update the color and font size properties for a specific parameter based on its value.

        Args:
            value (float): The value of the parameter to check.
            parameter_name (str): The name of the parameter to update color and font size for.
        """
        critical_threshold = getattr(self, f'critical_{parameter_name}_threshold')
        warning_threshold = getattr(self, f'warning_{parameter_name}_threshold')
        if value >= critical_threshold:
            setattr(self, f'{parameter_name}_alarm', CRITICAL)
        elif value >= warning_threshold:
            setattr(self, f'{parameter_name}_alarm', WARNING)


class HtmlTable:

    def __init__(self, parameters, alarm: Alarm):
        self.parameters = parameters
        self.alarm = alarm
        # Default color and font size for normal conditions
        self.default_font_color = "#10263b"
        self.default_background_color = "white"
        self.default_font_size = "font-size:12px"

        # Alarm color and font size for critical and warning conditions
        self.critical_color = "#ff5566"
        self.alarm_font_color = "white"
        self.warning_color = "#ffaa44"
        self.alarm_font_size = "font-size:14px"

    def display(self):
        # device_table = dmu_table(parameters) if device == 'dmu' else dru_table(parameters)
        device_table = self.if_board_table()
        channel_table = self._get_channel_freq_table()
        table = ""
        table += '<div class="sigma-container">'
        table += device_table + channel_table
        table += "</div>"
        return table

    def discovery_table(self):
        table = ""
        table += '<div class="sigma-container">'
        table += self.get_opt_connected_table()
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

    def ltel_board_table(self):

        table = ""
        table += '<div class="sigma-container">'
        table += self.get_power_table()
        table += self.get_vswr_temperature_table()
        table += self._get_ltel_board_channel_freq_table()
        table += "</div>"
        return table

    def if_board_table(self):
        table = ""
        table += self.get_opt_status_table()
        table += self.get_power_table()
        table += self.get_vswr_temperature_table()
        return table

    def _get_ltel_board_channel_freq_table(self):

        channel_bandwidth = self.parameters.get('channel_bandwidth', 0)
        uplink_start_frequency = self.parameters.get('uplink_start_frequency', 0)
        for channel in range(1, 17):
            channel_key = f"channel_{channel}"
            ul_ch_freq = uplink_start_frequency + self.parameters.get(f"{channel_key}_number", 0) * channel_bandwidth
            self.parameters[f"{channel_key}_freq"] = round(ul_ch_freq, 3)
        return self._get_channel_freq_table()

    def _get_channel_freq_table(self):
        """
        Generates HTML table with frequency and status data based on the working mode.

        Returns:
            table_html (str): HTML formatted string of the data table.

        If KeyError occurs during the operation, it prints an error message
        to stderr and exits with an UNKNOWN status. If a key is not found in self.parameters,
        it sets the respective parameter value to '-'.
        """
        # Initialize empty lists
        frequencies = []
        status = []

        try:
            # Fetch parameters with '.get()' and default to '-' if key not found
            working_mode = self.parameters.get('working_mode', '-')
            work_bandwidth = self.parameters.get("work_bandwidth", 0)
            uplink_start_frequency = self.parameters.get('uplink_start_frequency', 0)
            work_bandwidth = self.parameters.get('work_bandwidth', 0)
            central_frequency_point = self.parameters.get('central_frequency_point', 0)

            if central_frequency_point == 0:
                if uplink_start_frequency == 0 and work_bandwidth == 0:
                    central_frequency_point = 0
                else:
                    central_frequency_point = uplink_start_frequency + (work_bandwidth / 2.0)

                # Construct frequency and status lists
            for channel in range(1, 17):
                frequencies.append(self.parameters.get(f"channel_{channel}_freq", '-'))
                status.append(self.parameters.get(f"channel_{channel}_status", '-'))

        except Exception as e:
            sys.stderr.write(f"UNKNOWN - Error: {str(e)}")
            sys.exit(UNKNOWN)

        table_html = ""

        # Construct HTML table according to working mode
        if working_mode == 'Channel Mode':
            table_html += self._generate_channel_mode_table(frequencies, status)
        else:
            table_html += self._generate_other_mode_table(working_mode, work_bandwidth, central_frequency_point)

        return table_html

    def _generate_channel_mode_table(self, frequencies: list, status: list) -> str:
        """
        Generates HTML table for the 'Channel Mode'.

        Arguments:
            frequencies (list): List of frequency data.
            status  (list): List of status data.

        Returns:
            str: HTML formatted string of the data table.
        """

        if self.parameters['device'] == 'dmu_ethernet':
            frequency = "Downlink"
        else:
            frequency = "Uplink"

        table_html = f"<table width=100%>" \
                     f"<thead><tr style=font-size:11px>" \
                     f"<th width='5%'>Channel</font></th>" \
                     f"<th width='5%'>Status</font></th>" \
                     f"<th width='50%'>{frequency} [Mhz]</font></th>" \
                     f"</tr></thead><tbody>"

        for i in range(16):
            table_html += f"<tr align='center' style=font-size:12px>" + \
                          f"<td>{i + 1}</td>" + \
                          f"<td>{status[i]}</td>" + \
                          f"<td>{frequencies[i]}</td>" + \
                          "</tr>"

        return table_html + "</tbody></table>"

    def _generate_other_mode_table(self, working_mode: str,
                                   work_bandwidth: int,
                                   central_frequency_point: int) -> str:
        """
        Generates HTML table for working modes other than 'Channel Mode'.

        Arguments:
            working_mode (str): The working mode of the system.
            work_bandwidth (int): Work bandwidth data.
            central_frequency_point (int): Central frequency point data.

        Returns:
            str: HTML formatted string of the data table.
        """
        table_html = "<table width=90%>" + \
                     "<thead><tr style=font-size:12px>" + \
                     "<th width='10%'>Mode</font></th>" + \
                     "<th width='30%'>Work Bandwidth [Mhz]</font></th>" + \
                     "<th width='30%'>Central Frequency Point [Mhz]</font></th>" + \
                     "</tr></thead><tbody>" + \
                     "<tr align='center' style=font-size:12px>" + \
                     f"<td>{working_mode}</td>" + \
                     f"<td>{work_bandwidth}</td>" + \
                     f"<td>{central_frequency_point}</td>" + \
                     "</tr></tbody></table>"

        return table_html

    def get_power_table(self):
        """
        Generates an HTML table displaying power and attenuation information.
        Applies styling based on alarm conditions.

        Returns:
            str: The generated HTML table. In case of an error, an empty string is returned.
        """
        try:
            # retrieve and initialize styles
            default_style = f"style=font-size:12px"
            uplink_power_style = default_style
            downlink_power_style = default_style

            # Update uplink and downlink_power_style based on alarm statuses
            # _get_alarm_style is extrapolated to be a part of this class and hence we use self
            if self.alarm.uplink_power_alarm == CRITICAL:
                uplink_power_style = self._get_alarm_style(self.critical_color, self.alarm_font_size)
            elif self.alarm.uplink_power_alarm == WARNING:
                uplink_power_style = self._get_alarm_style(self.warning_color, self.alarm_font_size)

            if self.alarm.downlink_power_alarm == CRITICAL:
                downlink_power_style = self._get_alarm_style(self.critical_color, self.alarm_font_size)
            elif self.alarm.downlink_power_alarm == WARNING:
                downlink_power_style = self._get_alarm_style(self.warning_color, self.alarm_font_size)

            device = self.parameters.get('device', "")
            if device == "dmu_ethernet":
                uplink_attenuation_power = self.parameters.get('upAtt', "")
                downlink_attenuation_power = self.parameters.get('dlAtt', "")
                downlink_input_power = self.parameters.get('uplink_input_power', "")
                uplink_output_power = self.parameters.get('downlink_output_power', "")
                table = ("<table width=250>"
                     "<thead>"
                     "<tr align=\"center\" style=font-size:12px>"
                     "<th width='12%'>Link</font></th>"
                     "<th width='12%'>Direction</font></th>"
                     "<th width='33%'>Power</font></th>"
                     "<th width='10%'>Attenuation</font></th>"
                    "<th width='12%'>Direction</font></th>"
                    "<th width='12%'>Power</font></th>"
                     "</tr></thead>"
                     "<tbody>"
                     f"<tr align=\"center\" {uplink_power_style}><td>Uplink</td>"
                     f"<td>Output</td>"
                     f"<td>{uplink_output_power}[dBm]</td>"
                     f"<td>{uplink_attenuation_power}[dB]</td>"
                     f"<td>Input</td>"
                     f"<td>{round(uplink_output_power-uplink_attenuation_power,2)}[dBm]</td></tr>"
                     f"<tr align=\"center\"{downlink_power_style}><td>Downlink</td>"
                     f"<td>Input</td>"
                     f"<td>{downlink_input_power}[dBm]</td>"
                     f"<td>{downlink_attenuation_power}[dB]</td>"
                     f"<td>Output</td>"
                     f"<td>{round(downlink_input_power - downlink_attenuation_power,2)}[dBm]</td></tr>"
                     "</tbody></table>")
                return table
            else:
                uplink_attenuation_power = self.parameters.get('dlAtt', "")
                downlink_attenuation_power = self.parameters.get('upAtt', "")
                uplink_input_power = self.parameters.get('uplink_input_power', "")
                downlink_output_power = self.parameters.get('downlink_output_power', "")
            # Generate HTML structure according to given format
                table = ("<table width=250>"
                        "<thead>"
                        "<tr align=\"center\" style=font-size:12px>"
                        "<th width='12%'>Link</font></th>"
                        "<th width='12%'>Direction</font></th>"
                        "<th width='33%'>Power</font></th>"
                        "<th width='10%'>Attenuation</font></th>"
                        "<th width='12%'>Direction</font></th>"
                        "</tr></thead>"
                        "<tbody>"
                        f"<tr align=\"center\" {uplink_power_style}><td>Uplink</td>"
                        f"<td>Input</td>"
                        f"<td>{uplink_input_power}[dBm]</td>"
                        f"<td>{uplink_attenuation_power}[dB]</td></tr>"
                        f"<tr align=\"center\"{downlink_power_style}><td>Downlink</td>"
                        f"<td>Output</td>"
                        f"<td>{downlink_output_power}[dBm]</td>"
                        f"<td>{downlink_attenuation_power}[dB]</td></tr>"
                        "</tbody></table>")
                return table

        except (KeyError, AttributeError) as e:
            # Write error to stderr and exit with status UNKNOWN when there is an Exception
            sys.stderr.write(f"UNKNOWN - Error: {str(e)}")
            sys.exit(UNKNOWN)

    def _get_alarm_style(self, color, font_size):
        """
        Defines the HTML style string for alarms.

        Args:
            color (str): The color for the alarm string.
            font_size (str): The font size for the alarm string.

        Returns:
            str: The HTML style string.
        """
        return f"style=font-size:{font_size};color:{color}"

    def get_vswr_temperature_table(self):
        # Define default styling
        default_style = f"style=font-size:12px"
        temperature_style = default_style

        # Update styling based on alarm conditions
        if self.alarm.temperature_alarm is CRITICAL:
            temperature_style = self._get_alarm_style(self.critical_color, self.alarm_font_size)
        elif self.alarm.temperature_alarm is WARNING:
            temperature_style = self._get_alarm_style(self.warning_color, self.alarm_font_size)

        if 'temperature' in self.parameters:
            temperature = self.parameters.get('temperature', "")
        elif 'power_amplifier_temperature' in self.parameters:
            temperature = self.parameters.get('power_amplifier_temperature', "")
        else:
            temperature = ""

        # Define table header with styling
        table2 = \
            "<table width=10%>" \
            "<thead>" \
            "<tr  style=font-size:12px>" \
            "<th width='40%'>Temperature</font></th>" \
            "</tr>" \
            "</thead>"
        # Populate table body with power and attenuation values
        table2 += \
            "<tbody>" \
            f"<tr align=\"center\" {temperature_style}>" \
            f"<td>{temperature} [&deg;C] </td> " \
            "</tr>" \
            "</tbody></table>"
        return table2

    def _get_alarm_style(self, color, font_size):
        """
        Generates an inline CSS style string based on the provided color and font size.

        Args:
            color (str): The background color for alarm indication.
            font_size (str): The font size for alarm indication.

        Returns:
            str: The generated inline CSS style string
        """

        background_color = f"background-color:{color}"
        font_color = f"color:white"
        return f"style={background_color};{font_color};{font_size}"

    def get_opt_status_table(self):
        """
        Generates an HTML table displaying optical port status information.
        Determines the number of ports based on the device type.

        Returns:
            str: The generated HTML table.
        """
        try:
            # Attempt to fetch device parameter
            device = self.parameters["device"]

            # Determine the range for optical ports based on device type
            opt_range = self._get_opt_range(device)

            # Initiate HTML table string
            table = "<table width=280>"

            # Define HTML table header
            table += ("<thead><tr align=\"center\" style=font-size:12px>"
                      "<th width='12%'>Port</font></th>"
                      "<th width='22%'>Activation Status</font></th>"
                      "<th width='22%'>Connected Devices</font></th>"
                      "<th width='20%'>Transmission Status</font></th>"
                      "</tr></thead>")

            # Start HTML table body
            table += "<tbody>"

            for i in range(1, opt_range + 1):
                # Construct parameter keys for connected devices and transmission status
                connected_key = f"optical_port_devices_connected_{i}"
                transmission_status_key = f"opt_{i}_transmission_status"
                activation_status_key = f"opt_{i}_activation_status"
                # Try to fetch connected devices and transmission status from parameters
                connected = str(self.parameters.get(connected_key, ""))
                transmission_status = str(self.parameters.get(transmission_status_key, ""))
                activation_status = str(self.parameters.get(activation_status_key, ""))

                # Construct HTML table row with necessary information
                table += ("<tr align=\"center\" style=font-size:12px>"
                          f"<td>opt{i}</td>"
                          f"<td>{activation_status}</td>"
                          f"<td>{connected}</td>"
                          f"<td>{transmission_status}</td>"
                          "</tr>")

            # Close HTML table body and table
            table += "</tbody></table>"

            return table

        except (KeyError, TypeError) as e:
            # Print error message to stderr and exit with status UNKNOWN
            sys.stderr.write(f"UNKNOWN - Error: Invalid data in parameters - {e}")
            sys.exit(UNKNOWN)

    def get_opt_connected_table(self):
        """
        Generates an HTML table displaying optical port status information.
        Determines the number of ports based on the device type.

        Returns:
            str: The generated HTML table
        """
        # Retrieve device type and calculate the optical range
        device = self.parameters["device"]
        opt_range = self._get_opt_range(device)

        # Initialize the HTML table with a specified width
        table_html = "<table width='320'>"

        # Define table header with styling
        table_html += (
            "<thead>"
            "<tr align='center' style='font-size:12px;'>"
            "<th width='12%'>Port</th>"
        )

        # Add headers for remote port IDs
        for remote_number in range(1, 8 + 1):
            table_html += f"<th width='13%'>Remote {remote_number} id</th>"

        table_html += "</tr></thead>"

        # Populate table body with optical port information
        table_html += "<tbody>"
        for i in range(1, 4 + 1):
            # Construct key names to access parameter values
            connected_name = f"optical_port_devices_connected_{i}"
            opt = str(i)
            connected = self.parameters.get(connected_name, 0)

            table_html += (
                "<tr align='center' style='font-size:12px;'>"
                f"<td>opt{opt}</td>"
            )

            # Retrieve optical port device ID topology and populate IDs for connected devices
            opt_key = f"optical_port_device_id_topology_{opt}"
            for dru_connected in range(1, connected + 1):
                dru_connected_key = f"id_{dru_connected}"
                dru_id = self.parameters[opt_key].get(dru_connected_key, "-")
                table_html += f"<td>{dru_id}</td>"

            # Fill in placeholders for non-connected ports
            for id in range(connected + 1, 8 + 1):
                table_html += f"<td> - </td>"

            table_html += "</tr>"

        table_html += "</tbody></table>"

        return table_html

    def _get_opt_range(self, device):
        """
        Determines the number of optical ports based on the device type.

        Args:
            device (str): The device type (dmu_ethernet, dmu_serial, or dru_serial_service).

        Returns:
            int: The number of optical ports for the specified device
        """

        if device in ['dmu_ethernet', 'dmu_serial_service']:
            return 4
        elif device in ['dru_ethernet', 'dru_serial_service']:
            return 2
        else:
            return 4


class Graphite:
    def __init__(self, parameters):
        self.parameters = parameters

    def display(self):
        """
        Generates the appropriate output based on the device type.

        Returns:
            str: The generated output
        """
        if self.parameters['device'] in ['dmu_ethernet', 'dru_ethernet', 'dmu_serial_service']:
            return self.dmu_output()
        elif self.parameters['device'] in ['discovery_ethernet', 'discovery_serial', 'discovery_redboard_serial']:
            return self.discovery_output()
        elif self.parameters['device'] in ['dmu_serial_host', 'dru_serial_host']:
            return self.dmu_serial_single()
        else:
            return ""

    def dru_output(self):
        graphite = ""
        if self.parameters['downlink_output_power'] == 0.0:
            self.parameters['downlink_output_power'] = "-"
        else:
            self.parameters['downlink_output_power'] = str(self.parameters['downlink_output_power'])
        pa_temperature = "Temperature=" + str(self.parameters['temperature'])
        pa_temperature += ";" + str(self.parameters['warning_temperature_threshold'])
        pa_temperature += ";" + str(self.parameters['critical_temperature_threshold'])
        dl_str = f"Downlink={self.parameters['downlink_output_power']}"
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        dl_str += ";" + str(self.parameters['critical_uplink_threshold'])
        vswr = "VSWR=" + self.parameters['vswr']
        up_str = f"Uplink={self.parameters['uplink_input_power']}"
        up_str += ";" + str(self.parameters['warning_uplink_threshold'])
        up_str += ";" + str(self.parameters['critical_uplink_threshold'])
        rt = "RT=" + self.parameters['rt'] + ";1000;2000"
        graphite = rt + " " + pa_temperature + " " + dl_str + " " + vswr + " " + up_str
        return graphite

    def dmu_output(self):
        """
        Constructs a graphite string with parameters data.

        Returns:
            graphite (str): The constructed graphite string.

        If any exception occurs during the operation, it will print an error message
        to stderr and exits with an UNKNOWN status. If a key is not found in self.parameters,
        it sets the respective parameter value to '-'.
        """
        try:
            # Use dict.get to safely fetch values; defaults to '-' if key is not found

            device = self.parameters.get('device', "")
            if device == "dmu_ethernet":
                downlink_input_power = self.parameters.get('uplink_input_power', "-")
                uplink_output_power = self.parameters.get('downlink_output_power', "-")
                if isinstance(uplink_output_power, (int, float)) and uplink_output_power > 20:
                    uplink_output_power = "-"

                if isinstance(downlink_input_power, (int, float)) and downlink_input_power > 20:
                    downlink_input_power = "-"
                    
                critical_downlink_threshold = str(self.parameters.get('critical_downlink_threshold', '-'))
                warning_downlink_threshold = str(self.parameters.get('warning_downlink_threshold', '-'))
                critical_uplink_threshold = str(self.parameters.get('critical_uplink_threshold', '-'))
                warning_uplink_threshold = str(self.parameters.get('warning_uplink_threshold', '-'))

                temperature = str(self.parameters.get('temperature', '-'))
                warning_temperature_threshold = str(self.parameters.get('warning_temperature_threshold', '-'))
                critical_temperature_threshold = str(self.parameters.get('critical_temperature_threshold', '-'))

                # Structure graphite string using fetched parameters
                dl_str = f"Downlink={downlink_input_power};{warning_downlink_threshold};{critical_downlink_threshold}"
                up_str = f"Uplink={uplink_output_power};{warning_uplink_threshold};{critical_uplink_threshold}"
                temperature_str = f"Temperature={temperature};{warning_temperature_threshold};{critical_temperature_threshold}"
                graphite = f"{dl_str} {up_str} {temperature_str}"
            else:
                uplink_input_power = self.parameters.get('uplink_input_power', "-")
                downlink_output_power = self.parameters.get('downlink_output_power', "-")

                if isinstance(uplink_input_power, (int, float)) and uplink_input_power > 20:
                    uplink_input_power = "-"

                if isinstance(downlink_output_power, (int, float)) and downlink_output_power > 20:
                    downlink_output_power = "-"

                critical_downlink_threshold = str(self.parameters.get('critical_downlink_threshold', '-'))
                warning_downlink_threshold = str(self.parameters.get('warning_downlink_threshold', '-'))
                critical_uplink_threshold = str(self.parameters.get('critical_uplink_threshold', '-'))
                warning_uplink_threshold = str(self.parameters.get('warning_uplink_threshold', '-'))

                temperature = str(self.parameters.get('temperature', '-'))
                warning_temperature_threshold = str(self.parameters.get('warning_temperature_threshold', '-'))
                critical_temperature_threshold = str(self.parameters.get('critical_temperature_threshold', '-'))

                # Structure graphite string using fetched parameters
                dl_str = f"Downlink={downlink_output_power};{warning_downlink_threshold};{critical_downlink_threshold}"
                up_str = f"Uplink={uplink_input_power};{warning_uplink_threshold};{critical_uplink_threshold}"
                temperature_str = f"Temperature={temperature};{warning_temperature_threshold};{critical_temperature_threshold}"
                graphite = f"{dl_str} {up_str} {temperature_str}"

            return graphite

        except Exception as e:
            # Handle any unexpected exception, write error message to stderr & exit
            sys.stderr.write(f"UNKNOWN - Error: {str(e)}")
            sys.exit(UNKNOWN)

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


class PluginOutput:
    def __init__(self, parameters):
        self.parameters = parameters
        # Define a dictionary of command types and corresponding functions
        self.command_functions = {
            'dru_serial_service': self.dru_serial_display,
            'dru_serial_host': self.dru_serial_host_display,
            'dmu_serial_service': self.get_master_remote_service_message,
            'dmu_serial_host': self.dmu_serial_host_display,
            'dru_ethernet': self.get_master_remote_service_message,
            'dmu_ethernet': self.get_master_remote_service_message,
            'discovery_ethernet': self.discovery_display,
            'discovery_serial': self.discovery_display,
            'discovery_redboard_serial': self.discovery_display
        }

    def dru_serial_display(self):
        graphite = ""
        alarm = Alarm(self.parameters)
        exit_code = alarm.check_alarm()
        html_table = HtmlTable(self.parameters, alarm)
        graphite = Graphite(self.parameters)
        plugin_output_message = (html_table.ltel_board_table() + "|" + graphite.display())
        return exit_code, plugin_output_message

    def dru_serial_host_display(self):
        rt = self.parameters['rt']
        device_id = int(self.parameters["hostname"][3:])
        optical_port = self.parameters["optical_port"]
        if optical_port is None:
            exit_value = CRITICAL
            message = f"CRITICAL - No optical_port defined in service"
            return exit_value, message
        key_name = f"optical_port_device_id_topology_{optical_port}"
        optical_port_device_id_topology = self.parameters.get(key_name, None)
        exit_value = CRITICAL
        message = f"CRITICAL - No id {device_id} found"
        if optical_port_device_id_topology is not None:
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

        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        plugin_output_message = f"OK - RTA = {rt} ms | {graphite.display()}"
        exit_code = OK
        return exit_code, plugin_output_message

    def get_master_remote_service_message(self):

        graphite = ""
        alarm = Alarm(self.parameters)

        html_table = HtmlTable(self.parameters, alarm)
        graphite = Graphite(self.parameters)
        plugin_output_message = f"{html_table.display()}|{graphite.display()}"
        exit_code = alarm.check_exit_code()
        if self.parameters['cmd_type'] == 'single_set':
            plugin_output_message = "OK"
        return exit_code, plugin_output_message

    def discovery_display(self):
        rt = self.parameters['rt']
        dt = self.parameters['dt']
        alarm = Alarm(self.parameters)
        html_table = HtmlTable(self.parameters, alarm)
        graphite = Graphite(self.parameters)
        rt = round(float(rt), 2)
        dt = round(float(dt), 2)
        plugin_output_message = f"{html_table.discovery_table()}|{graphite.display()}"
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
    """
    Class responsible for discovering and creating DRU devices.
    """

    def __init__(self, parameters):
        """
        Initialize the Discovery object with the provided parameters.

        Args:
            parameters (dict): A dictionary containing discovery parameters.
        """

        self.parameters = parameters

        self.cmd_name_map = {
            1: DRSRemoteSerialCommand.optical_port_device_id_topology_1,
            2: DRSRemoteSerialCommand.optical_port_device_id_topology_2,
            3: DRSRemoteSerialCommand.optical_port_device_id_topology_3,
            4: DRSRemoteSerialCommand.optical_port_device_id_topology_4,
        }

    def search_and_create_dru(self):
        """Discover DRU based on device type."""

        device = self.parameters["device"]

        if device == "discovery_ethernet":
            self._discover_ethernet()
        elif device == "discovery_serial":
            self._discover_serial()
        elif device == "discovery_redboard_serial":
            self._discover_redboad_serial()
        else:
            return WARNING
        return OK

    def _get_director_instance(self):
        """
        Retrieve an instance of the Director class.

        Returns:
            Director: An instance of the Director class.
        """

        hostname = socket.gethostname()
        master_host = socket.gethostbyname(hostname)
        # master_host = '192.168.60.73'
        return Director(master_host)

    def _create_host_query(self, dru, device, imports, cmd_name=None, baud_rate=19200):
        """
        Generate a query for creating or updating hosts in Icinga 2 Director.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.
            device (str): The type of device to discover (e.g., "dru_ethernet", "dru_serial_host").
            imports (list): A list of imports for the host template.
            cmd_name (str, optional): The command name for serial devices. Defaults to None.

        Returns:
            dict: A query dictionary for creating or updating hosts in Icinga 2 Director.
        """

        query = {
            'object_name': dru.hostname,
            'object_type': 'object',
            'address': dru.ip_addr,
            'imports': imports,
            'display_name': dru.name,
            'vars': {
                'parents': [dru.parent],
                'device': device,
                'baud_rate': str(baud_rate)
            }
        }

        if cmd_name:
            query['vars']['cmd_name'] = cmd_name

        return query

    def _update_service_query(self, dru):
        """
        Generate a query for updating service status in Icinga 2 Director.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.

        Returns:
            dict: A query dictionary for updating service status in Icinga 2 Director.
        """

        return {
            'object_name': 'Status',
            'object_type': 'object',
            'vars': {
                'opt': str(dru.port),
                'dru': str(dru.position),
                'parents': [dru.parent]
            }
        }

    def _log_status(self, dru, message):
        """
        Log status messages to stderr.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.
            message (str): The status message to log.
        """

        sys.stderr.write(f"{dru} {message} \n")

    def _deploy_if_needed(self, director, response):
        """
        Deploy changes to Icinga 2 Director if the response status code indicates a need to deploy.

        Args:
            director (Director): An instance of the Director class.
            response (requests.Response): The response from the API call.
        """

        if response.status_code != 304:
            director.deploy()

    def _process_response(self, dru, message, response, director):
        """
        Process and log the response from Icinga 2 Director, and deploy changes if necessary.

        Args:
            dru (DRU): A DRU object representing the connected DRU device.
            message (str): The status message to log.
            response (requests.Response): The response from the API call.
            director (Director): An instance of the Director class.
        """
        if response.status_code != 304:
            # self._log_status(dru, message)
            self._deploy_if_needed(director, response)

    def _dru_connected_search(self):
        """
        Identify and gather information about connected DRU devices.

        This method iterates through the configured optical ports and retrieves
        information about the connected DRU devices. It constructs a dictionary
        storing the discovered DRU devices and their corresponding information.

        Returns:
            dict: A dictionary containing discovered DRU devices and their information.
        """

        hostname = self.parameters["hostname"]
        dru_connected = {}

        for opt in range(1, 5):
            port_name = f"optical_port_devices_connected_{opt}"
            optical_port_devices_connected = 0 if self.parameters[port_name] == "-" else self.parameters[port_name] + 1

            dru_connected[f"opt{opt}"] = []
            for connected in range(1, optical_port_devices_connected):
                fix_ip_start = 0xC0
                fix_ip_end_opt = [0, 100, 120, 140, 160]
                net = self.parameters["device_id"]
                id_key = f"optical_port_device_id_topology_{opt}"
                # device_id = self.parameters[id_key][f"id_{connected}"]
                device_id = self.parameters.get(id_key, {}).get(f"id_{connected}")
                parent = self._get_parent_name(hostname, dru_connected, opt, connected)
                ip = f"{fix_ip_start}.{net}.{fix_ip_end_opt[opt] + connected - 1}"

                if device_id == 0:
                    pass
                else:
                    d = DRU(connected, opt, device_id, hostname, ip, parent)
                    dru_connected[f"opt{opt}"].append(d)
                    connected_ip_addr_name = f"optical_port_connected_ip_addr_{opt}{connected}"
                    self.parameters[connected_ip_addr_name] = ip

        return dru_connected

    def _get_dru_connected_number(self):
        """
        Identify and gather information about connected DRU devices.

        This method iterates through the configured optical ports and retrieves
        information about the connected DRU devices. It constructs a dictionary
        storing the discovered DRU devices and their corresponding information.

        Returns:
            dict: A dictionary containing discovered DRU devices and their information.
        """
        # Get the hostname from the parameters
        hostname = self.parameters["hostname"]

        # Create an empty dictionary to store the connected DRU devices
        dru_connected = {}

        # Iterate through the optical ports
        for opt in range(1, 5):
            # Get the parameter name for the current optical port
            port_name = f"optical_port_devices_connected_{opt}"

            # Get the value of the parameter
            optical_port_devices_connected = 0 if self.parameters[port_name] == "-" else self.parameters[port_name]

            # Add the connected DRU device to the dictionary
            dru_connected[f"opt{opt}"] = optical_port_devices_connected

        # Return the dictionary containing the discovered DRU devices
        return dru_connected

    def _get_parent_name(self, hostname, dru_connected, opt, connected):
        """
        Gets the name of the parent according to the given conditions.

        Args:
            hostname (str): The name of the current host.
            dru_connected (dict): A dictionary containing information about the DRU connection.
            opt (int): The option to consider.
            connected (int): The connection status.

        Returns:
            str: The name of the parent or None if not found.

        """
        try:
            parent = hostname if connected == 1 else dru_connected[f"opt{opt}"][connected - 2].hostname
        except KeyError:
            # print("Key not found in dru_connected dictionary")
            parent = None
        except IndexError:
            # print("Index out of range in dru_connected list")
            parent = None
        except AttributeError:
            # print("Attribute error accessing .hostname")
            parent = None
        return parent

    def _discover_device(self, device, imports, cmd_name=None):
        """
        Handle device discovery for the specified device type.

        This method performs the discovery process for the given device type.
        It identifies connected DRU devices, creates the necessary host objects
        in Icinga 2 Director, and updates the parameters dictionary with
        the execution time.

        Args:
            device (str): The type of device to discover (e.g., "dru_ethernet", "dru_serial_host").
            imports (list): A list of imports for the host template.
            cmd_name (str, optional): The command name for serial devices. Defaults to None.
        """

        dt = time.time()
        director = self._get_director_instance()
        dru_connected = self._dru_connected_search()
        baud_rate = self.parameters['baud_rate']

        for opt in dru_connected:

            for dru in dru_connected[opt]:
                if dru.port in self.cmd_name_map:
                    cmd_name = self.cmd_name_map[dru.port]
                response = director.get_dru_name(dru)
                if response.status_code == 200:
                    text = response.text
                    data = json.loads(text)
                    dru.name = data.get('display_name', dru.name)

                director_query = self._create_host_query(dru, device, imports, cmd_name, baud_rate)
                update_query = self._create_host_query(dru, device, imports, cmd_name, baud_rate)

                response = director.create_host(director_query=director_query, update_query=update_query)
                message = "Create -> Success" if response.status_code == 200 else "Create -> " + str(response.text)

                self._process_response(dru, message, response, director)
                if response.status_code == 200:
                    self._modify_service_status()

        self.parameters["dt"] = str(time.time() - dt)

    def _discover_ethernet(self):
        """
        Perform discovery and creation for Ethernet DRU devices.

        This method handles the discovery process for Ethernet-based DRU devices.
        It creates the necessary host objects in Icinga 2 Director and deploys the changes.

        """

        device = "dru_ethernet"
        imports = ["ethernet-host-template"]
        self._discover_device(device, imports)

    def _discover_serial(self):
        """
        Perform discovery and creation for Serial DRU devices.

        This method handles the discovery process for Serial-based DRU devices.
        It creates the necessary host objects in Icinga 2 Director and deploys the changes.
        Additionally, it updates the service status for the discovered devices.

        """

        device = "dru_serial_host"
        imports = ["serial-host-template"]
        cmd_name = "254"
        self._discover_device(device, imports, cmd_name)

    def _modify_service_status(self):
        """
        Modify service status for devices discovered using serial discovery.

        Iterates through the connected DRU devices and constructs a query for updating
        the service status for each device. Sends the query to Icinga 2 Director and
        processes the response, logging status messages and deploying changes if necessary.
        """

        director = self._get_director_instance()
        dru_connected = self._dru_connected_search()

        for opt in dru_connected:
            for dru in dru_connected[opt]:
                director_query = self._update_service_query(dru)
                response = director.modify_service(director_query=director_query)

                message = (
                    f"Success - Service modified"
                    if response.status_code == 200
                    else f"Error - {response.text}"
                )

                self._process_response(dru, message, response, director)

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN
