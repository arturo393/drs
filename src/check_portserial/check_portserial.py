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

#--------------------------------
#-- Declaracion de constantes
#--------------------------------
C_HEADER = '7E'
C_MODULE_ADDRESS_ADDRESS = '00'
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
    -a, --action= ACTION: 02 = Query ; 03 = Set o write 
    -i, --interface= INTERFACE: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
    -c, --cmdNumber= CMDNUMBER: Comando a enviar
    -l, --cmdBodyLenght= CMDBODYLENGHT: Indentica si lee o escribe
    -d, --cmdData= CMDDATA: dato a escribir 
    -t, --crc=  CRC: Byte de control
    
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
    Interface = -1
    CmdNumber = -1
    CmdBodyLenght = -1
    CmdData = -1
    Crc = -1

    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "haicldt:",
            ["help", "port=", "action=", "interface=", "cmdNumber=", "cmdBodyLenght=", "cmdData=", "crc="]
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

        elif o in ("-i", "--interface"): 
            try:
                Interface = a                
            except ValueError:
                print('Interface invalido')
        
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

    if Interface == -1:
       sys.stderr.write("Error: La Interface es obligatorio\n")      
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

    if Crc == -1:
       sys.stderr.write("Error: Crc es obligatorio\n")      
       sys.exit(2)                                                      
            
    return Port, Action, Interface, CmdNumber, CmdBodyLenght, CmdData, Crc

#----------------------------------------------------
#-- Armar trama de escritura o lectura
#-- (PARAMETROS)
#-- Interface: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
#-- CmdNumber: 80 = Send ; 00 = Receive
#-- CmdBodyLenght: Indentica si lee o escribe
#-- CmdData: dato a escribir <integer en hex>
#-- Crc: Byte de control
#---------------------------------------------------
def obtener_trama(Interface, CmdNumber, CmdBodyLenght, CmdData, Crc):
    CmdNumber_hex = CmdNumber.encode('utf8').hex()
    CmdBodyLenght_hex = CmdBodyLenght.encode('utf8').hex()
    CmdData_hex = CmdData.encode('utf8').hex()
    Crc_hex = Crc.encode('utf8').hex()
    
    trama = str(C_HEADER + Interface + C_MODULE_ADDRESS_ADDRESS + C_DATA_TYPE + CmdNumber_hex + C_RESPONSE_FLAG + CmdBodyLenght_hex + CmdData_hex + Crc_hex + C_END)
    trama_out = str(C_HEADER + ' ' + Interface + ' ' + C_MODULE_ADDRESS_ADDRESS + ' ' + C_DATA_TYPE + ' ' + CmdNumber_hex + ' ' + C_RESPONSE_FLAG + ' ' + CmdBodyLenght_hex + ' ' + CmdData_hex + ' ' + Crc_hex + ' ' + C_END)
    
    print('La trama es: %s' % trama_out)
    return trama.encode('utf8')

#----------------------
#   MAIN
#----------------------
def main():
    
    #-- Analizar los argumentos pasados por el usuario
    Port, Action, Interface, CmdNumber, CmdBodyLenght, CmdData, Crc = analizar_argumentos()

    #-- Armando la trama
    Trama = obtener_trama(Interface, CmdNumber, CmdBodyLenght, CmdData, Crc)

    #--------------------------------------------------------
    #-- Abrir el puerto serie. Si hay algun error se termina
    #--------------------------------------------------------
    try:
        s = serial.Serial(Port, 9600,serial.EIGHTBITS)

        #-- Timeout: 1 seg
        s.timeout=1

    except serial.SerialException:
        #-- Error al abrir el puerto serie 
        sys.stderr.write("Error al abrir puerto %s \n" % str(Port))   
        sys.exit(1)

    #-- Mostrar el nombre del dispositivo
    print("Puerto (%s): (%s)" % (str(Port),s.portstr))

    if Action == "02":
        #-----------------------------------------------------
        #--  Action: Leer el puerto
        #--  Devuelve el puerto y otros argumentos enviados como parametros
        #-----------------------------------------------------
        print("aqui va el codigo")
        Result = s.read(serial.EIGHTBITS)
        print("(%s)" % str(Result))
        s.close()
        #-- leer el puerto
    elif Action == "03":
        print('Escribiendo en el puerto la trama: [%s]' % Trama)
        nBytes = s.write(Trama)        
        s.flush()
        print('numero de Bytes devueltos: %s' % str(nBytes))        
        Result = s.read(nBytes)        
        print("Leyendo el puerto: [%s]" % Result.decode('utf8'))
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