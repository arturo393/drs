#!/usr/bin/env python
import serial
from crccheck.crc import Crc16Xmodem

def getChecksum(cmd):
    """
    -Description: this fuction calculate the checksum for a given comand
    -param text: string with the data, ex device = 03 , id = 03 cmd = 0503110000
    -return: cheksum for the given command
    """
    data = bytearray.fromhex(cmd)

    crc = hex(Crc16Xmodem.calc(data))

    if (len(crc) == 5):
        checksum = crc[3:5] + '0' + crc[2:3]
    else:
        checksum = crc[4:6] + crc[2:4]
    return checksum

def main():    
    deviceId = 99
    cmd = hex(deviceId) 
    print('cmd')
    print(cmd)
    print('cmd2')
    print(cmd[2:3])
    cmd_string = '05' + '0' + cmd[2:3] + '110000'  # concatena trama
    print(cmd_string)
    checksum = getChecksum(cmd_string) # calcula CRC
    print(checksum)
    trama = '7E' + cmd_string + checksum + '7F'
    print(trama)
    cmd_bytes = bytearray.fromhex(trama)
    hex_byte = ''

    for cmd_byte in cmd_bytes:
        hex_byte = ("{0:02x}".format(cmd_byte))
        #ser.write(bytes.fromhex(hex_byte))
        
    #hexResponse = ser.read(21)
    data = ''
    #for i in range(0, 21):
    #    data.append(hexResponse[i])



if __name__ == "__main__":
    main()