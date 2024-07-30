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
import argparse

from src.plugins.drs.command_executor import CommandExecutor
from src.plugins.drs.definitions.nagios import CRITICAL, OK, WARNING
from src.plugins.drs.definitions.santone_commands import NearEndQueryCommandNumber
from src.plugins.drs.discovery import Discovery
from src.plugins.drs.plugin_output import PluginOutput
from src.plugins.drs.parameters import Parameters

# DMU_PORT = 'COM4'
# DRU_PORT = 'COM2'

# COM1_BAUD = 19200
# COM2_BAUD = 19200


# Detectar el sistema operativo


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
    -br, --baud_rate
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
        ap.add_argument("-a", "--address", required=False,
                        help="address es requerido", default="192.168.11.22")
        ap.add_argument("-d", "--device", required=True,
                        help="device es requerido", default="dmu")
        ap.add_argument("-n", "--hostname", required=True,
                        help="hostname es requerido", default="dmu0")
        ap.add_argument("-op", "--optical_port", required=False,
                        help="hostname es requerido", default="0")
        ap.add_argument("-dn", "--device_number", required=False,
                        help="device_number es requerido", default="0")
        ap.add_argument("-b", "--bandwidth", required=False,
                        help="bandwidth es requerido", default=0)
        ap.add_argument("-l", "--cmd_body_length", required=False,
                        help="hostname es requerido", default="0")
        ap.add_argument("-c", "--cmd_name", required=False, help="cmd_name es requerido",
                        default=NearEndQueryCommandNumber.device_id)
        ap.add_argument("-cd", "--cmd_data", required=False,
                        help="bandwidth es requerido", default=-1)
        ap.add_argument("-ct", "--cmd_type", required=False,
                        help="cmd_type es requerido", default="unknow")
        ap.add_argument("-br", "--baud_rate", required=False,
                        help="baud rate es requerido", default=19200)
        ap.add_argument("-wut", "--warning_uplink_threshold", required=False,
                        help="warning_uplink_threshold es requerido", default=200)
        ap.add_argument("-cut", "--critical_uplink_threshold", required=False,
                        help="critical_uplink_threshold es requerido", default=200)
        ap.add_argument("-wdt", "--warning_downlink_threshold", required=False,
                        help="warning_downlink_threshold es requerido", default=200)
        ap.add_argument("-cdt", "--critical_downlink_threshold", required=False,
                        help="critical_downlink_threshold es requerido", default=200)
        ap.add_argument("-wtt", "--warning_temperature_threshold", required=False,
                        help="warning_temperature_threshold es requerido", default=200)
        ap.add_argument("-ctt", "--critical_temperature_threshold", required=False,
                        help="critical_temperature_threshold es requerido", default=200)

        args = vars(ap.parse_args())

        # Check if the high level warning uplink value exists.
        if "warning_uplink_threshold" not in args:
            args["warning_uplink_threshold"] = 41

        # Check if the high level critical uplink value exists.
        if "critical_uplink_threshold" not in args:
            args["critical_uplink_threshold"] = 38

        # Check if the high level warning downlink value exists.
        if "warning_downlink_threshold" not in args:
            args["warning_downlink_threshold"] = 41

        # Check if the high level critical downlink value exists.
        if "critical_downlink_threshold" not in args:
            args["critical_downlink_threshold"] = 38

        # Check if the high level warning temperature value exists.
        if "warning_temperature_threshold" not in args:
            args["warning_temperature_threshold"] = 50

        # Check if the high level critical temperature value exists.
        if "critical_temperature_threshold" not in args:
            args["critical_temperature_threshold"] = 45

    except Exception as e:
        # print help information and exit:
        sys.stderr.write("CRITICAL - " + str(e) + "\n")
        cmd_help()
        sys.exit(CRITICAL)

    return args


def main():
    # Parse arguments
    global parameters
    args = args_check()
    device = args['device']
    cmd_type = args['cmd_type']

    discovery_commands = ["discovery_ethernet",
                          "discovery_serial", 'discovery_redboard_serial']
    dru_devices = ["dru_ethernet", 'dru_serial_host', 'dru_serial_service']
    dmu_devices = ["dmu_ethernet", 'dmu_serial_host', 'dmu_serial_service']

    all_commands = discovery_commands + dru_devices + dmu_devices

    if device in all_commands:
        executor = CommandExecutor(args)
        executor.execute(cmd_type)
        command = executor.get_command()
        if device in discovery_commands:
            deviceIdcommandData = command.get_commandData_by_commandNumber(NearEndQueryCommandNumber.device_id)
            parameters = Parameters(command.parameters)
            dru_connected = parameters.get_connected_dru()
            discovery = Discovery(command.parameters['baud_rate'], dru_connected)
            if discovery.discover_remotes(command.parameters) is not OK:
                sys.stderr.write(f"WARNING  - no output message for {device}")
                sys.exit(WARNING)

        plugin_output = PluginOutput(command.parameters)
        exit_code, plugin_output_message = plugin_output.create_message()
        sys.stderr.write(plugin_output_message)
        sys.exit(exit_code)
    else:
        sys.stderr.write("\nCRITICAL - " + "No drs device detected")
        sys.exit(CRITICAL)


if __name__ == "__main__":
    main()
