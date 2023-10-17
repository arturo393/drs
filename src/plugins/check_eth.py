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
import sys
from crccheck.crc import Crc16Xmodem
import argparse
import drs as drs


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
        ap.add_argument("-a", "--address", required=False, help="address es requerido", default="192.168.11.22")
        ap.add_argument("-d", "--device", required=True, help="device es requerido", default="dmu")
        ap.add_argument("-n", "--hostname", required=True, help="hostname es requerido", default="dmu0")
        ap.add_argument("-p", "--port", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-b", "--bandwidth", required=False, help="bandwidth es requerido", default=0)
        ap.add_argument("-l", "--cmd_body_length", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-c", "--cmd_name", required=False, help="hostname es requerido",
                        default=drs.NearEndQueryCommandNumber.device_id)
        ap.add_argument("-cd", "--cmd_data", required=False, help="bandwidth es requerido", default="0")
        ap.add_argument("-ct", "--cmd_type", required=False, help="cmd_type es requerido", default="unknow")
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
        sys.exit(drs.CRITICAL)

    return args


def main():
    # -- Analizar los argumentos pasados por el usuario
    global parameters
    args = args_check()
    address = args['address']
    device = args['device']
    hostname = args['hostname']
    cmd_name = int(args['cmd_name'])
    cmd_body_length = int(args['cmd_body_length'])
    cmd_type = args['cmd_type']

    if len(args['cmd_data']) > 1:
        cmd_data = args['cmd_data']
    else:
        cmd_data = int(args['cmd_data'])

    if device == "dru_ethernet" or device == "dmu_ethernet":
        command = drs.Command(device=device,
                              command_number=cmd_name,
                              command_body_length=cmd_body_length,
                              command_data=cmd_data,
                              args=args
                              )

        if cmd_type == "single_set":
            cmd_name = command.get_setting_command_value(cmd_name)
            command.set(command_body_length, command_data, cmd_name)
            parameters = command.transmit_and_receive_tcp(address)
            sys.stderr.write("OK")
            sys.exit(drs.OK)
        elif cmd_type == "group_query":
            if device == 'dmu_ethernet':
                command.query_group(DRSMasterCommand)
            elif device == 'dru_ethernet':
                command.query_group(DRSRemoteCommand)
            else:
                sys.stderr.write("CRITICAL - no device")
                sys.exit(CRITICAL)

            parameters = command.transmit_and_receive_tcp(address)
            plugin_output = drs.PluginOutput(command.parameters)
            plugin_output.device_display()
        elif cmd_type == "single_query":
            command.query_single(cmd_name)
            parameters = command.transmit_and_receive_tcp(address)
            plugin_output = drs.PluginOutput(command.parameters)
            plugin_output.device_display()
        else:
            sys.stderr.write("WARNING - no command type defined")
            sys.exit(drs.WARNING)

    elif device == "discovery_ethernet":
        command.query_group(DiscoveryCommand)
        parameters = command.transmit_and_receive_tcp(address)
        discovery = drs.Discovery(command.parameters)
        plugin_output = drs.PluginOutput(command.parameters)
        plugin_output.discovery_display()

    elif device == "dmu_serial":
        command = drs.Command(device=device,
                              command_number=cmd_name,
                              command_body_length=cmd_body_length,
                              command_data=cmd_data,
                              command_type=type,
                              args=args
                              )
        baud = 9600
        port = '/dev/ttyS0'
        #            port = 'COM4'
    elif device == 'dru_serial':
        baud = 9600
        port = '/dev/ttyS0'
    elif device == 'discovery_serial':
        baud = 9600
        port = '/dev/ttyS0'
    #    port = 'COM4'
    else:
        sys.stderr.write("\nCRITICAL - " + "No drs device detected")
        sys.exit(drs.CRITICAL)

        command.transmit_and_receive_serial(baud=baud, port=port)
        if command.cmd_number_ok == 0:
            sys.stderr.write("\nCRITICAL - " + "No reply")
            sys.exit(drs.CRITICAL)

        if type == drs.SET:
            sys.stderr.write("OK")
            sys.exit(drs.OK)
        elif type == drs.QUERY_SINGLE:
            plugin_output = drs.PluginOutput(command.parameters)
            plugin_output.dru_serial_host_display()
        else:
            if device == "dru" or device == "dmu":
                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.device_display()
            elif device == "discovery":
                discovery = drs.Discovery(command.parameters)
                discovery.serial()

                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.discovery_display()
            else:
                sys.stderr.write("\nOK - " + "no command")
                sys.exit(drs.OK)



if __name__ == "__main__":
    main()
