#!/usr/bin/env python
#
# RS485 plugin
#
import sys
import serial

# Help Message


def print_help():
    print("Usage: %s <deviceId> <command> [value]" % sys.argv[0])
    print("deviceId: a number between 0 and 255")
    print("command: status, read or write")
    print("value: optional, if command is write")
    sys.exit(3)

# Reads arguments from command line
#
# if no arguments are given, it will return a help message
# first and second argument are deviceId and command respectively
# third argument is optional, if it is given, it will be the value
# if second argument is 'write' and third argument is not given, it will return a help message


def read_arguments():
    if len(sys.argv) < 3:
        print_help()
    deviceId = int(sys.argv[1])
    command = sys.argv[2]
    if len(sys.argv) == 4:
        value = int(sys.argv[3])
    else:
        value = None
    return deviceId, command, value

# Open Serial Port
# If /dev/ttyUSB0 is not available, try open /dev/ttyUSB1


def open_serial_port(port='/dev/ttyUSB0'):
    try:
        ser = serial.Serial(port, 9600, timeout=1)
    except serial.SerialException:
        open_serial_port('/dev/ttyUSB1')
    except:
        exit(3)
    return ser

# Main
# execute logic
# Read arguments from command line
# Open serial port
# Send command to serial port
# Read response from serial port
# Close serial port


def main():
    deviceId, command, value = read_arguments()
    ser = open_serial_port()
    if command == 'status':
        ser.write(chr(deviceId) + chr(0x00))
    elif command == 'read':
        ser.write(chr(deviceId) + chr(0x01))
    elif command == 'write':
        ser.write(chr(deviceId) + chr(0x02) + chr(value))
    else:
        print_help()
    response = ser.read(20)
    print(ord(response))
    ser.close()
    exit(0)


if __name__ == "__main__":
    main()
# Nagios Exit Codes
# Exit Code	Status
# 0	OK
# 1	WARNING
# 2	CRITICAL
# 3	UNKNOWN
