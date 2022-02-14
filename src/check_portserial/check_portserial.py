#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

#----------------------------------------------------------------------------
# check_portserial.py  Ejemplo de manejo del puerto serie desde python utilizando la
# libreria multiplataforma pyserial.py (http://pyserial.sf.net)
#
#  Se envia una cadena por el puerto serie y se muestra lo que se recibe
#  Se puede especificar por la linea de comandos el puerto serie a 
#  a emplear
#
#  (C)2022 Guillermo Gonzalez (ggonzalez@itaum.com)
#  
#
#  LICENCIA GPL
#-----------------------------------------------------------------------------

import sys
import getopt
import serial
from crccheck.crc import Crc16Xmodem

#--------------------------------
#-- Declaracion de constantes
#--------------------------------
C_HEADER = '7E'
C_DATA_TYPE = '00'
C_RESPONSE_FLAG = '00'
C_END = '7E'
C_UNKNOWN2BYTE01 = '0101'
C_UNKNOWN2BYTE02 = '0100'
C_UNKNOWN1BYTE = '01'
C_TXRXS_80 = '80'
C_TXRXS_FF = 'FF'
C_TYPE_QUERY = '02'
C_TYPE_SET = '03'
C_RETURN = '0d'
C_SITE_NUMBER = '00000000'


#--------------------------------
#-- Imprimir mensaje de ayuda  
#--------------------------------
def help():
    sys.stderr.write("""Uso: check_portserial [opciones]
    Ejemplo de uso del puerto serie en Python

    opciones:
    -p, --port=  Puerto serie a leer o escribir Ej. /dev/ttyS0
    -a, --action= ACTION: query ; set 
    -d, --device= dmu, dru
    -x, --dmuDevice1= INTERFACE: ID de PA o DSP, Ej. F8, F9, FA, etc
    -y, --dmuDevice2= Device: DRU ID number, Ej. 80, E7, 41, etc
    -n, --cmdNumber= CMDNUMBER: Comando a enviar
    -l, --cmdBodyLenght= tamano del cuerpo en bytes, 1, 2.
    -c, --cmdData= CMDDATA: dato a escribir 
    -i, --druId= DRU ID number Ej. 0x11-0x16 / 0x21-0x26 / 0x31-36 / 0x41-46 

    
    Ejemplo:
    check_portserial.py -p COM0       --> Usar el primer puerto serie (Windows)
    check_portserial.py -p /dev/ttyS0 --> Especificar el dispositivo serie (Linux) 
    
    """)

#-----------------------------------------------------
#--  Analizar los argumentos pasados por el usuario
#--  Devuelve el puerto y otros argumentos enviados como parametros
#-----------------------------------------------------
def analizar_argumentos():

    Port = ""  
    Action = ""
    Device = ""
    DmuDevice1 = ""
    DmuDevice2 = ""
    CmdNumber = ""
    CmdBodyLenght = ""
    CmdData = ""
    DruId = ""

    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "hpadxynlci:",
            ["help", "port=", "action=", "device=", "dmuDevice1=", "dmuDevice2=", "cmdNumber=", "cmdBodyLenght=", "cmdData=", "druId="]
        )
        
    except getopt.GetoptError as e:
        # print help information and exit:
        print(e.msg)
        help()
        sys.exit(2)

    #-- Leer argumentos pasados
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit()
        
        elif o in ("-p", "--port"):                        
            Port = a  
        
        elif o in ("-a", "--action"): 
            Action = a 
        
        elif o in ("-d", "--device"): 
            Device = a    
        
        elif o in ("-x", "--dmuDevice1"): 
            DmuDevice1 = a  

        elif o in ("-y", "--dmuDevice2"): 
            DmuDevice2 = a   
        
        elif o in ("-c", "--cmdNumber"): 
            CmdNumber = a 

        elif o in ("-l", "--cmdBodyLenght"): 
            CmdBodyLenght = a   

        elif o in ("-c", "--cmdData"): 
            CmdData = a  

        elif o in ("-i", "--druId"): 
            DruId = a                
            
    #validamos los argumentos pasados    
    if Port == "":
       sys.stderr.write("Error: El puerto es obligatorio\n")      
       sys.exit(2) 

    if Device == "":
       sys.stderr.write("Error: El device es obligatorio\n")      
       sys.exit(2)
    
    if DmuDevice1 == "" and Device == 'dmu':
       sys.stderr.write("Error: El dmuDevice1 es obligatorio\n")      
       sys.exit(2)  

    if DmuDevice2 == "" and Device == 'dmu':
       sys.stderr.write("Error: El dmuDevice2 es obligatorio\n")      
       sys.exit(2)      

    if CmdNumber == "":
       sys.stderr.write("Error: cmdNumber es obligatorio\n")      
       sys.exit(2) 

    if (CmdBodyLenght == "" and Action == 'set') or (CmdBodyLenght == "" and Device == 'dru'):
       sys.stderr.write("Error: cmdBodyLenght es obligatorio\n")      
       sys.exit(2)  

    if (CmdData == "" and Action == 'set') or (CmdData == "" and Device == 'dru') :
       sys.stderr.write("Error: cmdData es obligatorio\n")      
       sys.exit(2)

    if (DruId == "" and Device == 'dru'):
       sys.stderr.write("Error: DruId es obligatorio\n")      
       sys.exit(2)     


    return Port, Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId

def getChecksum(cmd):
    """
    -Description: this fuction calculate the checksum for a given comand
    -param text: string with the data, ex device = 03 , id = 03 cmd = 0503110000
    -return: cheksum for the given command
    """
    data = bytearray.fromhex(cmd)
  
    crc = hex(Crc16Xmodem.calc(data))
    print("crc: %s" % crc)
    
    if (len(crc) == 5):
        checksum = crc[3:5] + '0' + crc[2:3]
    else:
        checksum = crc[4:6] + crc[2:4]
    print("checksum: %s" % checksum)  
    return checksum

#----------------------------------------------------
#-- Formateria formato cadena de byte a Hex
#--------------------------------------------------
def formatearHex(dato):
   
    if dato[0:2] == '0x':
       dato_hex = dato[2:] 
    else:
        dato_hex = dato

    return dato_hex
#----------------------------------------------------
#-- Armar trama de escritura o lectura
#-- (PARAMETROS)
#-- Interface: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
#-- CmdNumber: 80 = Send ; 00 = Receive
#-- CmdBodyLenght: Indentica si lee o escribe
#-- CmdData: dato a escribir <integer en hex>
#-- Crc: Byte de control
#---------------------------------------------------
def obtener_trama(Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId):      
    
    DmuDevice1_hex = formatearHex(DmuDevice1)    
    print('DmuDevice1_hex: %s' % DmuDevice1_hex)     

    DmuDevice2_hex = formatearHex(DmuDevice2)    
    print('DmuDevice2_hex: %s' % DmuDevice2_hex)      

    CmdNumber_hex = formatearHex(CmdNumber)        
    print('CmdNumber_hex: %s' % CmdNumber_hex)       
    
    print('CmdBodyLenght: %s' % CmdBodyLenght)      
    if (Device == 'dru'): 
        CmdBodyLenght_hex = formatearHex(CmdBodyLenght)  
              
        CmdData_hex = formatearHex(CmdData)          
        print('CmdData_hex: %s' % CmdData_hex)

        DruId_hex = formatearHex(DruId)   
        print('DruId_hex: %s' % DruId_hex)
        
        try:
            cant_bytes  = int(CmdBodyLenght_hex, 16)  
            print('cant_bytes: %s' % cant_bytes)           
        except ValueError:
            sys.stderr.write("Error: CmdBodyLenght no tiene formato hexadecimal\n")      
            sys.exit(2)     
        tramaLengthCodeData = CmdBodyLenght_hex + CmdNumber_hex + CmdData_hex
        print('tramaLengthCodeData: %s' % tramaLengthCodeData)     
        lenTramaLengthCodeData = int(len(tramaLengthCodeData)/2)
        print('lenTramaLengthCodeData: %s' % lenTramaLengthCodeData)     
        if lenTramaLengthCodeData != cant_bytes: 
            sys.stderr.write("Error: CmdBodyLenght + CmdNumber + CmdData, no corresponde a la cantidad de bytes indicados\n")      
            sys.exit(2)   

        Retunr_hex =  C_RETURN
        
    else:
        CmdBodyLenght_hex = '00'        
        Retunr_hex = ''
        if (Action == 'set'):
            CmdData_hex = formatearHex(CmdData)    
            print('CmdData_hex: %s' % CmdData_hex)   
        else:
            CmdData_hex = ''
    print('CmdNumber_hex: %s' % CmdNumber_hex)    
 
    print('Device: %s' % Device)
    if Device == 'dru':
        cmd_string = C_UNKNOWN2BYTE01 + C_SITE_NUMBER + DruId_hex + C_UNKNOWN2BYTE02 + C_TXRXS_80 + C_UNKNOWN1BYTE + C_TYPE_QUERY + C_TXRXS_FF + CmdBodyLenght_hex + CmdNumber_hex  + CmdData_hex
    else:
        cmd_string = DmuDevice1_hex + DmuDevice2_hex + C_DATA_TYPE + CmdNumber_hex  + C_RESPONSE_FLAG + CmdBodyLenght_hex + CmdData_hex
    
    print('La trama corta: %s' % cmd_string)
    checksum = getChecksum(cmd_string) # calcula CRC
   
    trama = C_HEADER + cmd_string + checksum +  C_END + Retunr_hex

    print('Query: %s' % trama)
    return str(trama)

def validar_trama_respuesta(hexResponse, Device):
    try:
        data = list() 
        
        if (
                hexResponse == None                
                or hexResponse == ""
                or hexResponse == " "
                or len(hexResponse) == 0
                or hexResponse[0] != 126
            ):
                sys.stderr.write("Error: trama de salida invalida\n" )      
                sys.exit(2) 
        if Device == 'dru':
            byte_respuesta = 14   #Para equipos remotos  de la trama
            cant_bytes_resp = int (hexResponse[byte_respuesta])
            rango_i = byte_respuesta + 3
            rango_n =  rango_i + cant_bytes_resp - 3
        else:
            byte_respuesta = 6    
            cant_bytes_resp = int (hexResponse[byte_respuesta])
            rango_i = byte_respuesta + 1
            rango_n =  rango_i + cant_bytes_resp
                      
        print('Cant Byte respuesta: %d' % cant_bytes_resp)             
        print('longitud trama: %d' % len(hexResponse))
        print('Rango i: %d' % rango_i)
        print('Rango n: %d' % rango_n)
        for i in range(rango_i, rango_n): 
            data.append(hexResponse[i])        
        return data          
    except ValueError:
        sys.stderr.write("Error: al leer trama de salida\n")      
        sys.exit(2)      

#----------------------
#   MAIN
#----------------------
def main():
    
    #-- Analizar los argumentos pasados por el usuario
    Port, Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId = analizar_argumentos()

    #-- Armando la trama
    Trama = obtener_trama(Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId)

    #--------------------------------------------------------
    #-- Abrir el puerto serie. Si hay algun error se termina
    #--------------------------------------------------------
    try:
        if Port == '/dev/ttyUSB0':
           baudrate = 19200
        else:
           baudrate = 9600  
        print('baudrate: %d' % baudrate)
        s = serial.Serial(Port, baudrate)

        #-- Timeout: 1 seg
        s.timeout=1

    except serial.SerialException:
        #-- Error al abrir el puerto serie 
        sys.stderr.write("Error al abrir puerto %s \n" % str(Port))   
        sys.exit(1)

    #-- Mostrar el nombre del dispositivo
    print("Puerto (%s): (%s)" % (str(Port),s.portstr))

    if Action == "query" or Action == "set":
        cmd_bytes = bytearray.fromhex(Trama)
        print(cmd_bytes)
        hex_byte = ''
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte))             
            s.write(bytes.fromhex(hex_byte))

        hexResponse = s.readline()
        #hexResponse = b'~\x07\x00\x00\xf8\x00\x008\x01\x00`r~'
        print("Answer: "+hexResponse.hex(chr(9)))
        ##Aqui se realiza la validacion de la respuesta
        data = validar_trama_respuesta(hexResponse, Device)
        
        if Action == 'set':
            if len(data) != 0:
                sys.stderr.write("Error: al escribir puerto %s \n" % str(Port))   
                sys.exit(2)
            else:    
               sys.stderr.write("OK\n")
        else:                
            print("Resultado de la Query es:")
            print(data)
            a_bytearray = bytearray(data)

            hex_string = a_bytearray.hex()
            sys.stderr.write(hex_string + '\n')          
        s.close()
    else:
        sys.stderr.write("Error: Accion invalida:  %s \n" % Action)      
        sys.exit(1)

if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code	Status
# 0	OK
# 1	WARNING
# 2	CRITICAL
# 3	UNKNOWN