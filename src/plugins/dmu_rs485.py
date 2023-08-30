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
    S_AD5662 = 0x04
    S_AFC = 0x06
    S_DATT = 0x08
    S_RESTORE_FACTORY_CONFIGURATION = 0x0a
    S_RESTORING_CONSISTENCY = 0x14
    S_5662_TEMPERATURE_COMPENSATION = 0x19
    S_VCXO_COMPENSATION_ENABLE_STEP_DELAY_REFERENCE_VALUE = 0x1d
    S_DAC0 = 0x25
    S_DAC1 = 0x27
    S_9524 = 0x29
    S_1197A = 0x2b
    S_1197B = 0x2d
    S_TEST_CONTROL_REGISTER = 0xc9
    S_ETH_IP_ADDRESS = 0xcb
    S_MODULE_EQUIPMENT_NUMBER = 0x16
    S_BROADBAND_SWITCHING_DIGITAL_FREQUENCY_SELECTION_AND_SUBBAND_SELECTION = 0x80


class QueryCommand(IntEnum):
    Q_VERSION_NUMBER = 0x01
    Q_TEMPERATURE = 0x02
    Q_HARDWARE_STATUS = 0x03
    Q_AD5662 = 0x05
    Q_AFC = 0x07
    Q_DATT = 0x09
    Q_VCXO_MANUAL = 0x0e
    Q_VCXO_COMPENSATION_ENABLE_STEP_DELAY_REFERENCE_VALUE = 0x1e
    Q_RX0_BROADBAND_POWER = 0x20
    Q_RX1_BROADBAND_POWER = 0x21
    Q_DAC0 = 0x26
    Q_DAC1 = 0x28
    Q_9524 = 0x2a
    Q_1197A = 0x2c
    Q_1197B = 0x2e
    Q_TEST_CONTROL_REGISTER = 0xca
    Q_ETH_IP_ADDRESS = 0xcc
    Q_MODULE_EQUIPMENT_NUMBER = 0xce
    Q_BROADBAND_SWITCHING = 0x81


class DigitalBoardCommand(IntEnum):
    DRU_NUMBER_OPT1 = 0xf8
    DRU_NUMBER_OPT2 = 0xf9
    DRU_NUMBER_OPT3 = 0xfa
    DRU_NUMBER_OPT4 = 0xfb
    INPUT_POWER = 0xf3
    CHANNEL_ACTIVATION_STATUS = 0x42
    CHANEL_FREQUENCY_POINT_CONFIGURATION = 0x36
    WORKING_MODE = 0x81
    GAIN_POWER_CONTROLL_ATT = 0xef
    OPTICAL_PORT_STATE = 0x91
    OPTICAL_PORT_STATUS_QUERY = 0x9a


class IfBoardSetCmd(IntEnum):
    RESTORE_FACTORY_CONFIG = 0x0a
    VERSION_NUMBER = 0x01
    RESTORE_CONSISTENCY = 0x14


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

        if command_number in [cmd_name.value for cmd_name in SettingCommand]:
            cmd_unit = self.cmd_unit_set()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"
        elif command_number in [cmd_name.value for cmd_name in QueryCommand]:
            cmd_unit = self.cmd_unit_query()
            crc = get_checksum(cmd_unit)
            self.query = f"{self.START_FLAG}{cmd_unit}{crc}{self.START_FLAG}"
        else:
            self.query = ""

    def __str__(self):
        if self.reply:
            reply = bytearray_to_hex(self.reply)
            message = self.get_reply_message()
            decode = self.extract_data_and_decode()
        else:
            reply = "No reply"
            message = ""
            decode = ""

        return f"{self.query} -  {reply} - {message} - {decode}"

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

    def extract_data_and_decode(self):
            """Extract data from a bytearray and decode it.

            Args:
                data: The bytearray to extract data from.

            Returns:
                The decoded data.
            """
            start_index = 0
            module_function_index = 1
            module_addr_index = 2
            data_type_index = 3
            cmd_number_index = 4
            respond_flag_index = 5
            cmd_body_length_index = 6
            cmd_data_index = 7

            module_function = self.reply[module_function_index]
            data_type = self.reply[data_type_index]
            command_number = self.reply[cmd_number_index]
            response_flag = self.reply[respond_flag_index]
            command_body_length = self.reply[cmd_body_length_index]
            command_body = self.reply[cmd_data_index:cmd_data_index + command_body_length]

            if response_flag != ResponseFlag.SUCCESS:
                return ""
                # Decode the command body
            elif command_number == QueryCommand.Q_VERSION_NUMBER:
                fpga_version_number = command_body[:4]
                fpga_version_number = self.decode_version(fpga_version_number)
                software_version_number = command_body[4:]
                software_version_number = self.decode_version(software_version_number)
                return f"FPGA version number: {fpga_version_number}, Software version number: {software_version_number}"
            elif command_number == QueryCommand.Q_TEMPERATURE:
                val = int.from_bytes(command_body, byteorder='little')
                if val > 125000:
                    temp = ((val * 2 / 1000) & 0xff) / 2
                else:
                    temp = val / 1000
                return f"Temperature: {temp} \℃"
            elif command_number == QueryCommand.Q_HARDWARE_STATUS:
                status = ["Locked" if i else "Loss of lock" for i in command_body]
                return f"Hardware status: {status}"
            elif command_number == QueryCommand.Q_AD5662:
                parameter = int.from_bytes(command_body[:2], byteorder='little')
                mode = "Automatic" if command_body[2] == 0 else "Manual"
                return f"AD5662: parameter {parameter}, mode {mode}"
            elif command_number == QueryCommand.Q_AFC:
                mode = "Automatic" if command_body[0] == 0 else "Manual"
                automatic_mode_optical_port = command_body[1]
                manual_mode_optical_port = command_body[2]
                return f"AFC: mode {mode}, automatic mode optical port {automatic_mode_optical_port}, manual mode optical port {manual_mode_optical_port}"
            elif command_number == QueryCommand.Q_DATT:
                channels = [i / 4 for i in command_body]
                return f"DATT: channels {channels}"

            elif command_number == QueryCommand.Q_ETH_IP_ADDRESS:
                ip_addr = self.decode_ip_address(command_body[:4])
                return ip_addr
    def decode_version(self,data):

        if len(data) == 5:
            year = data[4]
            month = data[3]
            day = data[2]
            version_number = data[1]
            module_type = data[0]
        else:
            year = data[3]
            month = data[2]
            day = data[1]
            version_number = data[0]
            module_type = 0x00
        # Convert year to full year format
        year += 2000


        # Convert module type to string
        if module_type == 0x0a:
            module_type = "near end machine"
        elif module_type == 0x0b:
            module_type = "remote end machine"
        else:
            module_type = "unknown"

        return f"Year: {year}, Month: {month}, Day: {day}, Version Number: {version_number}, Module Type: {module_type}"

    def decode_ip_address(self,
                          data):
        ip_address = ".".join(str(b) for b in data)
        return ip_address
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


# ----------------------
#   MAIN
# ----------------------
def main():
    # -- Analizar los argumentos pasados por el usuario
    hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl = analizar_argumentos()

    cmd_list = list()
    # Create a list of command data objects.
    # Create a list of command data objects.
    for cmd_name in QueryCommand:
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
    target_ip = '192.168.11.22'  # Replace with the actual IP address
    target_port = 80  # Replace with the actual port number

    replies = list()

    for cmd in cmd_list:
        start_time = time.time()
        rs485.write_serial_frame(cmd.query, serial)
        cmd.reply = rs485.read_serial_frame(serial)
        print(cmd)

        replies.append(cmd.reply)
        tmp = time.time() - start_time
        time.sleep(tmp)
        query = bytearray.fromhex(cmd.query)



    #     try:
    #         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #         client_socket.settimeout(1)
    #         client_socket.connect((target_ip, target_port))
    #         client_socket.send(query)
    #         reply_data = client_socket.recv(1024)  # You can adjust the buffer size

    #         # Print the received data
    #         print("Received data:", reply_data.hex())

    #     except socket.timeout:
    #         print("Timeout occurred: No response received within the specified timeout.")

    #     except socket.error as e:
    #         print("Socket error:", e)

    # client_socket.close()
    serial.close()

    # messages =  list(zip(queries,str_replies))

    #     parameters = rs485.getParametersFromDmuMessages(messages)
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


if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN
