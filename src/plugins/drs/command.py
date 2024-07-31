import os
import time
import serial
import socket
import sys

from typing import Optional
from typing import Tuple

from src.plugins.drs.comunication_protocol.comunication_protocol import CommunicationProtocol
from src.plugins.drs.definitions.nagios import WARNING, CRITICAL, OK, UNKNOWN
from src.plugins.drs.definitions.santone_commands import DRSRemoteCommand, DiscoveryCommand, DRSMasterCommand, DiscoveryRedBoardCommand, SettingCommand, NearEndQueryCommandNumber, HardwarePeripheralDeviceParameterCommand, RemoteQueryCommandNumber
from src.plugins.drs.definitions.ltel_commands import CommBoardGroupCmd, CommBoardCmd
from src.plugins.drs.comunication_protocol.ltel.ltel_protocol import LtelProtocol
from src.plugins.drs.comunication_protocol.ltel.ltel_protocol_group import LTELProtocolGroup
from src.plugins.drs.comunication_protocol.santone_protocol import SantoneProtocol


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
        self.parameters['warning_uplink_threshold'] = int(
            args['warning_uplink_threshold'])
        self.parameters['critical_uplink_threshold'] = int(
            args['critical_uplink_threshold'])
        self.parameters['warning_downlink_threshold'] = int(
            args['warning_downlink_threshold'])
        self.parameters['critical_downlink_threshold'] = int(
            args['critical_downlink_threshold'])
        self.parameters['warning_temperature_threshold'] = int(
            args['warning_temperature_threshold'])
        self.parameters['critical_temperature_threshold'] = int(
            args['critical_temperature_threshold'])

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
        cmd_data = CommunicationProtocol()

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
            sys.stderr.write(
                f"UNKNOWN - Invalid start address format: {address}")
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

    def get_commandData_by_commandNumber(self , command_number):
        for commandData in self.list:
            if commandData.command_number == command_number:
                return commandData
        return None

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
                    LtelProtocol(dru_id, cmd_name, 0x02)
                    self.list.append(LtelProtocol(dru_id, cmd_name, 0x02))

            elif cmd_group == CommBoardGroupCmd:
                opt = self.parameters['optical_port']
                dru = self.parameters['device_number']
                dru_id = f"{opt}{dru}"
                for cmd in cmd_group:
                    self.list.append(LTELProtocolGroup(dru_id, cmd))
            else:
                for cmd_name in cmd_group:
                    santone_protocol = SantoneProtocol(cmd_name, 0x00, -1)
                    self.list.append(santone_protocol)
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
        cmd_data = CommunicationProtocol()
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
        for message in self.list:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((address, self.tcp_port))
                    sock.settimeout(2)
                    sock.sendall(message.get_command_query_as_bytearray())
                    data_received = sock.recv(1024)
                    sock.close()
                    if message.save_if_valid(data_received):
                        reply_counter = reply_counter + 1
                    time.sleep(0.1)
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
            self.serial = self.set_serial_with_timeout(
                port, baud, timeout=timeout)
        except serial.SerialException:
            sys.stderr.write(
                f"CRITICAL - The specified port {port} is not available at {baud}")
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
            sys.stderr.write(
                f"CRITICAL - The specified port {port} is not available at {baud}")
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
            sys.stderr.write(
                f"CRITICAL - Invalid hexadecimal format for the frame {Trama}")
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
            value = command.get_reply_value()
            # Update the parameters with the decoded data.
            if value:
                decoded_commands += 1
                self.parameters.update(value)

        return decoded_commands

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
                    sys.stderr.write(
                        "CRITICAL - " + (e.args.__str__()) + str(port))
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
                    sys.stderr.write(
                        "CRITICAL - " + (e.args.__str__()) + str(port))
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
