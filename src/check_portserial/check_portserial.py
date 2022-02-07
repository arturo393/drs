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

#--------------------------------
#-- Imprimir mensaje de ayuda  
#--------------------------------
def help():
    sys.stderr.write("""Uso: check_portserial [opciones]
    Ejemplo de uso del puerto serie en Python

    opciones:
    -p, --port=  PORT o DEVICE: Puerto serie a leer o escribir Ej. /dev/ttyS0
    -a, --action= ACTION: read = Query ; write = Set o write 
    -i, --dmuId= INTERFACE: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
    -d, --druId= DIVICE: DRU ID number, En la trama MODULE_ADDRESS_FUNCTION
    -n, --cmdNumber= CMDNUMBER: Comando a enviar
    -l, --cmdBodyLenght= CMDBODYLENGHT: Indentica si lee o escribe
    -c, --cmdData= CMDDATA: dato a escribir 

    
    Ejemplo:
    check_portserial.py -p COM0       --> Usar el primer puerto serie (Windows)
    check_portserial.py -p /dev/ttyS0 --> Especificar el dispositivo serie (Linux) 
    
    """)

#-----------------------------------------------------
#--  Analizar los argumentos pasados por el usuario
#--  Devuelve el puerto y otros argumentos enviados como parametros
#-----------------------------------------------------
def analizar_argumentos():

    Port = -1   
    Action = ""
    DmuId = -1
    DruId = -1
    CmdNumber = -1
    CmdBodyLenght = -1
    CmdData = -1

    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "hpaidnlc:",
            ["help", "port=", "action=", "dmuId=", "druId=", "cmdNumber=", "cmdBodyLenght=", "cmdData="]
        )
    except getopt.GetoptError:
        # print help information and exit:
        help()
        sys.exit(2)

    #-- Leer argumentos pasados
    for o, a in opts:
        if o in ("-h", "--help"):
            help()
            sys.exit()
        
        elif o in ("-p", "--port"): 
            try:                
                Port = a               
            except ValueError:
                print('Puerto invalido')
        
        elif o in ("-a", "--action"): 
            try:
                Action = a                
            except ValueError:
                print('Accion invalida')  

        elif o in ("-i", "--dmuId"): 
            try:
                DmuId = a                
            except ValueError:
                print('dmuId es invalido')

        elif o in ("-d", "--druId"): 
            try:
                DruId = a                
            except ValueError:
                print('druId es invalido invalido')        
        
        elif o in ("-c", "--cmdNumber"): 
            try:
                CmdNumber = a                
            except ValueError:
                print('Data invalida')

        elif o in ("-l", "--cmdBodyLenght"): 
            try:
                CmdBodyLenght = a                
            except ValueError:
                print('cmdBodyLenght invalida')

        elif o in ("-c", "--cmdData"): 
            try:
                CmdData = a                
            except ValueError:
                print('cmdData invalida')  

        elif o in ("-t", "--crc"): 
            try:
                Crc = a                
            except ValueError:
                print('crc invalida') 
    if Port == -1:
       sys.stderr.write("Error: El puerto es obligatorio\n")      
       sys.exit(2) 

    if DmuId == -1:
       sys.stderr.write("Error: El DMU es obligatorio\n")      
       sys.exit(2)  

    if DruId == -1:
       sys.stderr.write("Error: El DRU es obligatorio\n")      
       sys.exit(2)      

    if CmdNumber == -1:
       sys.stderr.write("Error: CmdNumber es obligatorio\n")      
       sys.exit(2) 

    if CmdBodyLenght == -1:
       sys.stderr.write("Error: CmdBodyLenght es obligatorio\n")      
       sys.exit(2)  

    if CmdData == -1:
       sys.stderr.write("Error: CmdData es obligatorio\n")      
       sys.exit(2) 


    return Port, Action, DmuId, DruId, CmdNumber, CmdBodyLenght, CmdData

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
#-- Armar trama de escritura o lectura
#-- (PARAMETROS)
#-- Interface: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
#-- CmdNumber: 80 = Send ; 00 = Receive
#-- CmdBodyLenght: Indentica si lee o escribe
#-- CmdData: dato a escribir <integer en hex>
#-- Crc: Byte de control
#---------------------------------------------------
def obtener_trama(DmuId, DruId, CmdNumber, CmdBodyLenght, CmdData):

    DmuId_hex = DmuId.encode('utf8').hex() #hex(int(DmuId))  # debe completar 1Byte
    DruId_hex = DruId.encode('utf8').hex()  # Completar 1 byte
    CmdNumber_hex = CmdNumber.encode('utf8').hex() #1 Byte
    CmdBodyLenght_hex = CmdBodyLenght.encode('utf8').hex()  #Logitud del comando en bytes
    CmdData_hex = CmdData.encode('utf8').hex()
    cmd_string = DmuId_hex + DruId_hex + C_DATA_TYPE + CmdNumber_hex  + C_RESPONSE_FLAG + CmdBodyLenght_hex + CmdData_hex
    print('La trama corta: %s' % cmd_string)
    checksum = getChecksum(cmd_string) # calcula CRC
   
    trama = C_HEADER + cmd_string + checksum +  C_END

    print('La trama es: %s' % trama)
    return str(trama)


#----------------------
#   MAIN
#----------------------
def main():
    
    #-- Analizar los argumentos pasados por el usuario
    Port, Action, DmuId, DruId, CmdNumber, CmdBodyLenght, CmdData = analizar_argumentos()

    #-- Armando la trama
    Trama = obtener_trama(DmuId, DruId, CmdNumber, CmdBodyLenght, CmdData)

    #--------------------------------------------------------
    #-- Abrir el puerto serie. Si hay algun error se termina
    #--------------------------------------------------------
    try:
        s = serial.Serial(Port, 9600)

        #-- Timeout: 1 seg
        s.timeout=1

    except serial.SerialException:
        #-- Error al abrir el puerto serie 
        sys.stderr.write("Error al abrir puerto %s \n" % str(Port))   
        sys.exit(1)

    #-- Mostrar el nombre del dispositivo
    print("Puerto (%s): (%s)" % (str(Port),s.portstr))

    if Action == "read":
        #-----------------------------------------------------
        #--  Action: Leer el puerto
        #--  Devuelve el puerto y otros argumentos enviados como parametros
        #-----------------------------------------------------
        print("aqui va el codigo")
        Result = s.read(serial.EIGHTBITS)
        print("(%s)" % str(Result))
        s.close()
        #-- leer el puerto
    elif Action == "write":
        cmd_bytes = bytearray.fromhex(Trama)
        print(cmd_bytes)
        hex_byte = ''
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte))            
            s.write(bytes.fromhex(hex_byte))

        # ---- Read from serial
        hexResponse = s.read(21)
        print("GET: "+hexResponse.hex('-'))
        
        s.close()
    else:
        sys.stderr.write("Accion invalida:  %s \n" % Action)      
        sys.exit(1)

if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code	Status
# 0	OK
# 1	WARNING
# 2	CRITICAL
# 3	UNKNOWN