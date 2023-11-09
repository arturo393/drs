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

COM1_BAUD = 115200


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
    cmd_name: int = int(args['cmd_name'])
    cmd_body_length = int(args['cmd_body_length'])
    cmd_type = args['cmd_type']

    if len(args['cmd_data']) > 1:
        cmd_data = args['cmd_data']
    else:
        cmd_data = int(args['cmd_data'])

    command = drs.Command(args=args)

    if device == "dru_ethernet" or device == "dmu_ethernet":
        command = drs.Command(args=args)
        if cmd_type == "single_set":
            command.create_single_set()
            parameters = command.transmit_and_receive_tcp(address)
            sys.stderr.write("OK")
            sys.exit(drs.OK)

        elif cmd_type == "group_query":
            if command.create_group_query() == 0:
                sys.stderr.write("CRITICAL - no device")
                sys.exit(drs.CRITICAL)
            parameters = command.transmit_and_receive_tcp(address)

        elif cmd_type == "single_query":
            cmd_name = command.get_command_value()
            command.create_single_query(cmd_name)
        else:
            sys.stderr.write("WARNING - no command type defined")
            sys.exit(drs.WARNING)

        command.transmit_and_receive_tcp(address)
        plugin_output = drs.PluginOutput(command.parameters)
        exit_code, plugin_output_message = plugin_output.get_master_remote_service_message()
        sys.stderr.write(plugin_output_message)
        sys.exit(exit_code)

    elif device == "discovery_ethernet":

        command.create_query_group(drs.DiscoveryCommand)
        parameters = command.transmit_and_receive_tcp(address)
        discovery = drs.Discovery(command.parameters)
        discovery.ethernet()
        plugin_output = drs.PluginOutput(command.parameters)
        plugin_output.discovery_display()

    elif device == "dmu_serial":
        if cmd_type == "single_set":
            cmd_name = command.get_setting_command_value(cmd_name)
            command.create_single_set(cmd_body_length, cmd_data, cmd_name)
            if command.transmit_and_receive_serial(baud=COM1_BAUD, port='/dev/ttyS0') == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                sys.stderr.write("OK")
                sys.exit(drs.OK)
        elif cmd_type == "group_query":
            command.create_query_group(drs.DRSMasterCommand)
            command.transmit_and_receive_serial(baud=COM1_BAUD, port='/dev/ttyS0')
            if command.cmd_number_ok == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.master_remote_service_display()
        elif cmd_type == "single_query":
            cmd_name = command.get_command_value(cmd_name)
            command.create_single_query(cmd_name)
            command.transmit_and_receive_serial(baud=COM1_BAUD, port='/dev/ttyS0')
            if command.cmd_number_ok == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.dmu_serial_host_display()

        else:
            sys.stderr.write("WARNING - no command type defined")
            sys.exit(drs.WARNING)

    elif device == 'dru_serial_service':
        command = drs.Command(device=device, args=args)
        if cmd_type == "single_set":
            cmd_name = command.get_command_value(cmd_name)
            command.create_single_set(cmd_body_length, cmd_data, cmd_name)
            sys.stderr.write(str(command.parameters))
            if command.transmit_and_receive_serial(baud=19200, port='/dev/ttyS0') == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                sys.stderr.write("OK")
                sys.exit(drs.OK)
        elif cmd_type == "group_query":
            command.create_query_group(drs.LtelDruCommand)
            command.transmit_and_receive_serial(baud=9600, port='/dev/ttyS1')
            if command.cmd_number_ok == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.master_remote_service_display()
        elif cmd_type == "single_query":
            cmd_name = command.get_command_value(cmd_name)
            command.create_single_query(cmd_name)
            if command.transmit_and_receive_serial(baud=19200, port='/dev/ttyS0') == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.dmu_serial_host_display()
        else:
            sys.stderr.write("WARNING - no command type defined")
            sys.exit(drs.WARNING)

    elif device == 'dru_serial_host':
        command = drs.Command(device=device, args=args)
        if cmd_type == "single_set":
            cmd_name = command.get_command_value(cmd_name)
            command.create_single_set(cmd_body_length, cmd_data, cmd_name)
            if command.transmit_and_receive_serial(baud=9600, port='/dev/ttyS0') == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                sys.stderr.write("OK")
                sys.exit(drs.OK)
        elif cmd_type == "group_query":
            command.create_query_group(drs.DRSRemoteSerialCommand)
            command.transmit_and_receive_serial(baud=9600, port='/dev/ttyS0')
            if command.cmd_number_ok == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.dru_serial_host_display()
        elif cmd_type == "single_query":
            optical_port = command.parameters['optical_port']
            if optical_port == 1:
                command.create_single_query(drs.DRSRemoteSerialCommand.optical_port_device_id_topology_1)
            elif optical_port == 2:
                command.create_single_query(drs.DRSRemoteSerialCommand.optical_port_device_id_topology_2)
            elif optical_port == 3:
                command.create_single_query(drs.DRSRemoteSerialCommand.optical_port_device_id_topology_3)
            elif optical_port == 4:
                command.create_single_query(drs.DRSRemoteSerialCommand.optical_port_device_id_topology_4)
            else:
                sys.stderr.write("\nWARNING - " + "Unknonw optical port")
                sys.exit(drs.WARNING)

            if command.transmit_and_receive_serial(baud=COM1_BAUD, port='/dev/ttyS0') == 0:
                sys.stderr.write("\nCRITICAL - " + "No reply")
                sys.exit(drs.CRITICAL)
            else:
                plugin_output = drs.PluginOutput(command.parameters)
                plugin_output.dru_serial_host_display()


        else:
            sys.stderr.write("WARNING - no command type defined")
            sys.exit(drs.WARNING)

    elif device == 'discovery_serial':
        command = drs.Command(device=device, args=args)
        command.create_query_group(drs.DiscoveryCommand)
        command.transmit_and_receive_serial(baud=COM1_BAUD, port='/dev/ttyS0')
        if command.cmd_number_ok == 0:
            sys.stderr.write("\nCRITICAL - " + "No reply")
            sys.exit(drs.CRITICAL)
        discovery = drs.Discovery(command.parameters)
        discovery.serial()
        plugin_output = drs.PluginOutput(command.parameters)
        plugin_output.discovery_display()

    else:
        sys.stderr.write("\nCRITICAL - " + "No drs device detected")
        sys.exit(drs.CRITICAL)


if __name__ == "__main__":
    main()
