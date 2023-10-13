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
        ap.add_argument("-c", "--cmd_name", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-cd", "--cmd_data", required=False, help="bandwidth es requerido", default="0")
        ap.add_argument("-t", "--type", required=False, help="bandwidth es requerido", default="0")
        ap.add_argument("-ct", "--comm_type", required=False, help="comm_type es requerido", default=0)
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
    args = args_check()
    address = args['address']
    device = args['device']
    hostname = args['hostname']
    port = int(args['port'])
    cmd_name = int(args['cmd_name'])
    cmd_body_length = int(args['cmd_body_length'])
    type = int(args['type'])
    comm_type = int(args['comm_type'])

    if len(args['cmd_data']) > 1:
        cmd_data = args['cmd_data']
    else:
        cmd_data = int(args['cmd_data'])

    command = drs.Command(device=device,
                          command_number=cmd_name,
                          command_body_length=cmd_body_length,
                          command_data=cmd_data,
                          command_type=type,
                          args=args
                          )
    if comm_type == drs.ETHERNET:
        parameters = command.transmit_and_receive_tcp(address)
    elif comm_type == drs.SERIAL:
        parameters = command.transmit_and_receive_serial(baud=19200, port='/dev/ttyS0')

    if type == drs.SET:
        sys.stderr.write("OK")
        sys.exit(drs.OK)
    else:
        if device == "dru" or device == "dmu":
            plugin_output = drs.PluginOutput(parameters)
            plugin_output.device_display()
        elif device == "discovery":
            discovery = drs.Discovery(parameters)
            discovery.ethernet()
            plugin_output = drs.PluginOutput(parameters)
            plugin_output.discovery_display()
        else:
            sys.stderr.write("\nOK - " + "no command")
            sys.exit(drs.OK)


if __name__ == "__main__":
    main()
