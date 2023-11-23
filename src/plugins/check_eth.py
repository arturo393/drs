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

import drs as drs


#DMU_PORT = 'COM4'
#DRU_PORT = 'COM2'

#COM1_BAUD = 19200
#COM2_BAUD = 19200

import os

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
        ap.add_argument("-op", "--optical_port", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-dn", "--device_number", required=False, help="device_number es requerido", default="0")
        ap.add_argument("-b", "--bandwidth", required=False, help="bandwidth es requerido", default=0)
        ap.add_argument("-l", "--cmd_body_length", required=False, help="hostname es requerido", default="0")
        ap.add_argument("-c", "--cmd_name", required=False, help="cmd_name es requerido",
                        default=drs.NearEndQueryCommandNumber.device_id)
        ap.add_argument("-cd", "--cmd_data", required=False, help="bandwidth es requerido", default=-1)
        ap.add_argument("-ct", "--cmd_type", required=False, help="cmd_type es requerido", default="unknow")
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
        sys.exit(drs.CRITICAL)

    return args


def main():

    platform = os.name
    COM1_BAUD = 19200
    COM2_BAUD = 19200
        
    # Realizar acciones basadas en el sistema operativo
    if platform == 'posix':  # Posix indica que es un sistema tipo Unix, como Linux
        DMU_PORT = '/dev/ttyS0'
        DRU_PORT = '/dev/ttyS1'
    elif platform == 'nt':  # 'nt' indica que es Windows
        DMU_PORT = 'COM4'
        DRU_PORT = 'COM2'
    else:
        # Acción por defecto para otros sistemas operativos
        print("Sistema operativo no identificado, ejecutando acción predeterminada.")
    # -- Analizar los argumentos pasados por el usuario
    global parameters
    args = args_check()
    address = args['address']
    device = args['device']
    cmd_name: int = int(args['cmd_name'])
    cmd_body_length = int(args['cmd_body_length'])
    cmd_type = args['cmd_type']
    
    if device in ["dru_ethernet", "dmu_ethernet", "discovery_ethernet", 'discovery_serial', 'dmu_serial_host',
                  'dmu_serial_service', 'dru_serial_host', 'dru_serial_service','discovery_redboard_serial']:
        command = drs.Command(args=args)
        is_created = command.create_command(cmd_type)
        if is_created == -1:
            sys.stderr.write("CRITICAL - no command type defined")
            sys.exit(drs.CRITICAL)
        elif is_created == -2:
            sys.stderr.write(f"CRITICAL - no command {args['cmd_name']} known")
            sys.exit(drs.CRITICAL)
        elif is_created == -3:
            sys.stderr.write(f"CRITICAL - no command group known")
            sys.exit(drs.CRITICAL)

        if device in ['dmu_serial_host', 'dmu_serial_service', 'dru_serial_host','discovery_serial','discovery_redboard_serial']:
            if not command.transmit_and_receive_serial(baud=COM1_BAUD, port=DMU_PORT):
                sys.stderr.write(f"CRITICAL - no response from {DMU_PORT} at {COM1_BAUD}")
                sys.exit(drs.CRITICAL)
        elif device in ['dru_serial_service']:
            if not command.transmit_and_receive_serial(baud=COM2_BAUD, port=DRU_PORT):
                sys.stderr.write(f"CRITICAL - no response from {DRU_PORT} at {COM2_BAUD}")
                sys.exit(drs.CRITICAL)
        else:
            if not command.transmit_and_receive_tcp(address):
                sys.stderr.write(f"CRITICAL - no response from {address}")
                sys.exit(drs.CRITICAL)

        if not command.extract_and_decode_received():
            sys.stderr.write(f"CRITICAL - no decoded data")
            sys.exit(drs.CRITICAL)

        if device in ["discovery_ethernet", "discovery_serial",'discovery_redboard_serial']:
            discovery = drs.Discovery(command.parameters)
            if discovery.search_and_create_dru() is not drs.OK:
                sys.stderr.write(f"WARNING  - no output message for {device}")
                sys.exit(drs.WARNING)

        plugin_output = drs.PluginOutput(command.parameters)
        exit_code, plugin_output_message = plugin_output.create_message()
        sys.stderr.write(plugin_output_message)
        sys.exit(exit_code)
    else:
        sys.stderr.write("\nCRITICAL - " + "No drs device detected")
        sys.exit(drs.CRITICAL)


def create_single_set_command(command):
    command_number = command.get_command_value()
    command_body_length = command.parameters['command_body_length']
    command_data = command.parameters['command_data']
    cmd_data = drs.CommandData()
    frame_len = cmd_data.generate_ifboard_frame(
        command_number=command_number,
        command_body_length=command_body_length,
        command_data=command_data,
    )
    if frame_len > 0:
        command.list.append(cmd_data)


if __name__ == "__main__":
    main()
