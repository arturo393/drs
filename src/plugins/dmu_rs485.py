#!/usr/bin/env python
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

import cmd
import dis
import sys
import getopt
import serial
from crccheck.crc import Crc16Xmodem
import argparse
import check_rs485 as rs485
import os
# import dru_discovery as discovery
import time
import socket
import codecs

from enum import IntEnum


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
    BROADBAND_SWITCHING_DIGITAL_FREQUENCY_SELECTION_AND_SUBBAND_SELECTION = 0x80


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
    #  q_module_equipment_number = 0xce
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
    central_frequency_point = 0x22
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
    central_frequency_point_2 = 0xeb
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


class DigitalBoardCommand(IntEnum):
    optical_port_devices_connected_1 = 0xf8
    optical_port_devices_connected_2 = 0xf9
    optical_port_devices_connected_3 = 0xfa
    optical_port_devices_connected_4 = 0xfb
    input_and_output_power = Tx0QueryCmd.input_and_output_power
    channel_switch = Rx0QueryCmd.channel_switch
    channel_frequency_configuration = Rx0QueryCmd.channel_frequency_configuration
    broadband_switching = HardwarePeripheralDeviceParameterCommand.broadband_switching
    gain_power_control_att = Tx0QueryCmd.gain_power_control_att
    optical_port_switch = NearEndQueryCommandNumber.optical_port_switch
    optical_port_status = NearEndQueryCommandNumber.optical_port_status


DONWLINK_MODULE = 0 << 7
UPLINK_MODULE = 1 << 7


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
    checksum_new = checksum.replace('7F', '5E7E')

    return checksum_new

    # Add more query command functions


class CommandData:
    START_FLAG = "7E"
    END_FLAG = "7F"

    def __init__(self, module_address, module_link, module_function, command_number, command_data, command_type,
                 response_flag, command_body_length):
        """
        Initialize the command data object.

        Args:
            module_address: The module address.
            module_link: The module link.
            module_function: The module function.
            command_number: The command number.
            command_data: The command data.
            command_type: The command type.
            response_flag: The response flag.
            command_body_length: The command body length.
        """

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
        elif command_number in [cmd_name.value for cmd_name in DigitalBoardCommand]:
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
            return f"Command number {command_number:02X} is not supported."

    @staticmethod
    def _decode_version_number(command_body):
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

        return fpga_version_number, software_version_number

    @staticmethod
    def _decode_temperature(command_body):
        val = int.from_bytes(command_body, byteorder='little')
        if val > 125000:
            temp = ((val * 2 / 1000) & 0xff) / 2
        else:
            temp = val / 1000
        return f"Temperature: {temp} \?"

    @staticmethod
    def _decode_hardware_status(command_body):
        status = ["Locked" if i else "Loss of lock" for i in command_body]
        return f"Hardware status: {status}"

    @staticmethod
    def _decode_ad5662(command_body):
        parameter = int.from_bytes(command_body[:2], byteorder='little')
        mode = "Automatic" if command_body[2] == 0 else "Manual"
        return f"AD5662: parameter {parameter}, mode {mode}"

    @staticmethod
    def _decode_afc(command_body):
        mode = "Automatic" if command_body[0] == 0 else "Manual"
        automatic_mode_optical_port = command_body[1]
        manual_mode_optical_port = command_body[2]
        return f"AFC: mode {mode}, automatic mode optical port {automatic_mode_optical_port}, manual mode optical port {manual_mode_optical_port}"

    @staticmethod
    def _decode_daatt(command_body):
        channels = [i / 4 for i in command_body]
        return f"DATT: channels {channels}"

    @staticmethod
    def _decode_eth_ip_address(command_body):
        ip_address = ".".join(str(b) for b in command_body)
        return ip_address

    @staticmethod
    def _decode_broadband_switching(command_body):
        if command_body[0] == 2:
            return "broadband"
        elif command_body[0] == 3:
            return "narrowband"
        else:
            return "unknown"

    @staticmethod
    def _decode_optical_port_devices_connected_1(command_body):
        return "opt1: "+Queries.decode_optical_port_devices_connected(command_body)

    @staticmethod
    def _decode_optical_port_devices_connected_2(command_body):
        return "opt2: "+Queries.decode_optical_port_devices_connected(command_body)

    @staticmethod
    def _decode_optical_port_devices_connected_3(command_body):
        return "opt3: "+Queries.decode_optical_port_devices_connected(command_body)

    @staticmethod
    def _decode_optical_port_devices_connected_4(command_body):
        return "opt4: "+Queries.decode_optical_port_devices_connected(command_body)

    @staticmethod
    def decode_optical_port_devices_connected(command_body):
        return str(command_body[0])

    @staticmethod
    def _decode_optical_port_device_id_topology_1(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return device_ids

    @staticmethod
    def _decode_optical_port_device_id_topology_2(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return device_ids

    @staticmethod
    def _decode_optical_port_device_id_topology_3(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return device_ids

    @staticmethod
    def _decode_optical_port_device_id_topology_4(command_body):
        device_ids = Queries.decode_optical_port_device_id_topology(command_body)
        return device_ids

    @staticmethod
    def decode_optical_port_device_id_topology(command_body):
        """Decodes the opticalportx_topology_id command."""
        port_number = command_body[0]
        device_ids = []
        for i in range(0, len(command_body), 2):
            device_id = command_body[i] + command_body[i + 1] * 256
            device_ids.append(device_id)
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
            device_macs = []
            for i in range(1, len(command_body), 4):
                device_mac = command_body[i:i + 4]
                mac_address = ""
                for byte in device_mac:
                    mac_address += f"{byte:02X}:"
                device_macs.append(mac_address)

            return device_macs
        except IndexError:
            print("Error: The command body is empty.")
            return ""


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3


# --------------------------------
# -- Imprimir mensaje de ayuda
# --------------------------------
def help():
    sys.stderr.write("""Uso: check_portserial [opciones]
    Ejemplo de uso del puerto serie en Python

    opciones:
    -lwul, --port   Puerto serie a leer o escribir Ej. /dev/ttyS0
    -a, --action  ACTION: query ; set
    -d, --device  dmu, dru
    -x, --dmuDevice1  INTERFACE: ID de PA o DSP, Ej. F8, F9, FA, etc
    -y, --dmuDevice2  Device: DRU ID number, Ej. 80, E7, 41, etc
    -n, --cmdNumber  CMDNUMBER: Comando a enviar
    -l, --cmdBodyLenght  tamano del cuerpo en bytes, 1, 2.
    -c, --cmdDat CMDDATA: dato a escribir
    -i, --druId DRU ID number Ej. 0x11-0x16 / 0x21-0x26 / 0x31-36 / 0x41-46
    """)


def analizar_argumentos():
    # -----------------------------------------------------
    # --  Analizar los argumentos pasados por el usuario
    # --  Devuelve el puerto y otros argumentos enviados como parametros
    # -----------------------------------------------------
    # Construct the argument parser
    ap = argparse.ArgumentParser()
    # Add the arguments to the parser
    # ap.add_argument("-h", "--help", required=False,  help="help")
    ap.add_argument("-hlwu", "--highLevelWarningUplink", required=False, help="highLevelWarningUplink es requerido",
                    default=200)
    ap.add_argument("-hlcu", "--highLevelCriticalUplink", required=False, help="highLevelCriticalUplink es requerido",
                    default=200)
    ap.add_argument("-hlwd", "--highLevelWarningDownlink", required=False, help="highLevelWarningDownlink es requerido",
                    default=200)
    ap.add_argument("-hlcd", "--highLevelCriticalDownlink", required=False,
                    help="highLevelCriticalDownlink es requerido", default=200)

    try:
        args = vars(ap.parse_args())
    except getopt.GetoptError as e:
        # print help information and exit:
        print(e.msg)
        help()
        sys.exit(1)

    HighLevelWarningUL = int(args['highLevelWarningUplink'])
    HighLevelCriticalUL = int(args['highLevelCriticalUplink'])
    HighLevelWarningDL = int(args['highLevelWarningDownlink'])
    HighLevelCriticalDL = int(args['highLevelCriticalDownlink'])

    return HighLevelWarningUL, HighLevelCriticalUL, HighLevelWarningDL, HighLevelCriticalDL


def get_ltel_queries():
    frame_list = list()
    function = "80"
    frame_list.append(rs485.obtener_trama('query', 'dmu', 'function', '00', 'f8', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', 'f9', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', 'fa', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', 'fb', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', 'f3', '00', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', 'ef', '00', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', 'b9', '00', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', '81', '00', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', '36', '00', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', '42', '00', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', '9a', '00', '00', '00'))
    frame_list.append(rs485.obtener_trama('query', 'dmu', '07', '00', '91', '00', '00', '00'))
    return frame_list


def get_alarm_from_dict(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameter_dict):
    if (parameter_dict['dlOutputPower'] != '-'):
        dlPower = float(parameter_dict['dlOutputPower'])
    else:
        dlPower = -200
    if (parameter_dict['ulInputPower'] != '-'):
        ulPower = float(parameter_dict['ulInputPower'])
    else:
        ulPower = -200

    alarm = ""
    if dlPower >= hl_critical_dl:
        alarm += "<h3><font color=\"#ff5566\">Downlink Power Level Critical "
        alarm += parameter_dict['dlOutputPower']
        alarm += " [dBm]!</font></h3>"
    elif dlPower >= hl_warning_dl:
        alarm += "<h3><font color=\"#ffaa44\">Downlink Power Level Warning "
        alarm += parameter_dict['dlOutputPower']
        alarm += "[dBm]</font></h3>"

    if ulPower > 0:
        alarm += ""
    elif ulPower >= hl_critical_ul:
        alarm += "<h3><font color=\"#ff5566\">Uplink Power Level Critical "
        alarm += parameter_dict['ulInputPower']
        alarm += "[dBm]!</font></h3>"
    elif ulPower >= hl_warning_ul:
        alarm += "<h3><font color=\"#ffaa44\">Uplink Power Level Warning "
        alarm += parameter_dict['ulInputPower']
        alarm += "[dBm]</font></h3>"

    return alarm


def get_graphite_str(hlwul, hlcul, hlwdl, hlcdl, parameter_dict):
    rt = parameter_dict['rt']

    rt_str = "RT=" + rt
    rt_str += ";" + str(1000)
    rt_str += ";" + str(2000)

    dl_str = "Downlink=" + parameter_dict['dlOutputPower']
    dl_str += ";" + str(hlwdl)
    dl_str += ";" + str(hlcdl)
    graphite = rt_str + " " + dl_str
    return graphite


def create_table(responseDict):
    table1 = get_opt_status_table(responseDict)
    table2 = get_power_table(responseDict)
    table3 = get_channel_table(responseDict)

    table = ""
    table += '<div class="sigma-container" >'
    table += table1 + table2 + table3
    table += "</div>"
    # tableport = '<div class="port-container" >'+table1+"</div>"
    # powertable = '<div class="port-container2" >'+table2+"</div>"
    # channeltable = '<div class="port-container3" >'+table3+"</div>"
    return table


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
        table3 += "<th width='10%'>Bandwidth [Mhz]</font></th>"
        table3 += "<th width='40%'>UpLink [Mhz]</font></th>"
        table3 += "<th width='40%'>Downlink [Mhz]</font></th>"
        table3 += "</tr></thead><tbody>"
        table3 += "<tr align=\"center\" style=font-size:12px>"
        table3 += "<td>" + responseDict['workingMode'] + "</td>"

        table3 += "<td>" + responseDict['Bandwidth'] + "</td>"
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
        opt = str(i)
        table1 += "<tr align=\"center\" style=font-size:12px>"
        table1 += "<td>opt" + opt + "</td>"
        table1 += "<td>" + responseDict['opt' + opt + 'ActivationStatus'] + "</td>"
        table1 += "<td>" + responseDict['opt' + opt + 'ConnectedRemotes'] + "</td>"
        table1 += "<td>" + responseDict['opt' + opt + 'TransmissionStatus'] + "</td>"
        table1 += "</tr>"

    table1 += "</tbody>"
    table1 += "</table>"
    return table1


# ----------------------
#   MAIN
# ----------------------
def main():
    # -- Analizar los argumentos pasados por el usuario
    hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl = analizar_argumentos()

    cmd_list = list()
    query = Queries()
    setting = Settings()
    # Create a list of command data objects.
    # Create a list of command data objects.
    for cmd_name in DigitalBoardCommand:
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

    # queries = getQueries()
    start_time = time.time()
    response_time = 0
    # serial = rs485.setSerial('/dev/ttyS0',19200)
    serial = rs485.setSerial('COM4', 19200)
    # Create a socket
    # Define the target IP address and port
    target_ip = '192.168.11.60'  # Replace with the actual IP address
    target_port = 65050  # Replace with the actual port number

    replies = list()
    for cmd_name in cmd_list:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((target_ip, target_port))
                sock.settimeout(1)
                data_bytes = bytearray.fromhex(cmd_name.query)
                sock.sendall(data_bytes)
                data_received = sock.recv(1024)
                sock.close()
                cmd_name.reply = data_received
        except Exception as e:
            print(e)

    for cmd_name in cmd_list:
        print(cmd_name)
        cmd_name.extract_data()
        message = Queries.decode(cmd_name.command_number, cmd_name.reply_command_data)
        print(message)

    #   messages =  list(zip(queries,str_replies))

    #   parameters = rs485.getParametersFromDmuMessages(messages)
    #    parameters = rs485.getParametersFromDmuReplies(queries, replies)

    #    response_time = time.time() - start_time
    # parameters["rt"] = str(response_time)
    # alarm = get_alarm_from_dict(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameters)
    # parameter_html_table = create_table(parameters)
    # graphite = get_graphite_str(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameters)

    # sys.stderr.write(alarm+parameter_html_table+"|"+graphite)
    return 0
    if (alarm != ""):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN
