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
    hex_val = '00'

    print(int(hex_val, 16))


    a_bytearray = bytearray([50, 100, 150, 200, 250])

    hex_string = a_bytearray.hex()

    print(hex_string)
    tamano_trama = 13
    cantidad_bytes = 3
    hexResponse = b'~\x07\x00\x00\xf8\x00\x008\x01\x00`r~'
    print("GET: "+hexResponse.hex('-'))    
    result = hexResponse.hex()


    print('longitud: %d' % len(hexResponse))
    print('pos 6: %s' % hexResponse[6])
    data = list()   
    for i in range(7, 7+cantidad_bytes): 
       print('CmdBodyLenght result: %s' % str(hexResponse[i]))
       data.append(hexResponse[i])    
    print(data)

    a_bytearray = bytearray(data)

    hex_string = a_bytearray.hex()

    print(hex_string)

    if ((
            (len(hexResponse) > tamano_trama)
            or (len(hexResponse) < tamano_trama)
            or hexResponse == None
            or hexResponse == ""
            or hexResponse == " "
        ) or (
            hexResponse[0] != 126
            and hexResponse[tamano_trama-1] != 126
        ) ):
            print('hubo un error al leer el dispositivo')
    #num = '99'.encode('utf8').hex()
    #print('Num: %s' % num)  
    #f_num = bytearray.fromhex(num)

    #for cmd_byte_f in f_num:
    #    print('Byte-k: %s' % chr(cmd_byte_f))  
    #    print('Byte-j: %s' % hex(cmd_byte_f))  
    #    print('--------------------------------')   
   
    #num = '7E003933'
    #f_num = bytearray.fromhex(num)

    #for cmd_byte_f in f_num:
    #    print('Byte-5: %s' % chr(cmd_byte_f))  
    #    print('Byte-5: %s' % hex(cmd_byte_f))  
    #    print('--------------------------------')   

    byte = '0x3101'
    print('cadena: %s' % byte[0:2])
    if byte[0:2] == '0x':
        print('result: %s' % byte[2:])
    else:
        print('no')   

if __name__ == "__main__":
    main()