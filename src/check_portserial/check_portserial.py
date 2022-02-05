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
#-- Imprimir mensaje de ayuda  
#--------------------------------
def help():
    sys.stderr.write("""Uso: check_portserial [opciones]
    Ejemplo de uso del puerto serie en Python

    opciones:
    -p, --port=PORT: Puerto serie a leer o escribir Ej. /dev/ttyS0 
    -d, --device=DEVICE:  ID del MCU o RDUx. 
    -a, --action=ACTION: 02 = Query ; 03 = Set o write
    -o, --object=OBJECT: ID de objeto, voltaje, temperatura, etc.
    -r, --data=DATA: valor a escribir 
    
    Ejemplo:
    check_portserial.py -p COM0       --> Usar el primer puerto serie (Windows)
    check_portserial.py -p /dev/ttyS0 --> Especificar el dispositivo serie (Linux) 
    
    """)

#-----------------------------------------------------
#--  Analizar los argumentos pasados por el usuario
#--  Devuelve el puerto y otros argumentos enviados como parametros
#-----------------------------------------------------
def Analizar_argumentos():

    Port = -1
    Device = -1
    Action = ""
    Object = -1
    Data = -1

    try:
        opts, args = getopt.getopt(sys.argv[1:],
            "hpdaor:",
            ["help", "port=", "device=", "action=", "object=", "data="]
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
        elif o in ("-d", "--device"): 
            try:
                Device = a                
            except ValueError:
                print('Dispositivo invalido')  
        elif o in ("-a", "--action"): 
            try:
                Action = a                
            except ValueError:
                print('Accion invalida')  
        elif o in ("-r", "--data"): 
            try:
                Data = a                
            except ValueError:
                print('Data invalida')           
            
    return Port, Device, Action, Object, Data


#----------------------
#   MAIN
#----------------------
def main():
    #-- Analizar los argumentos pasados por el usuario
    Port, Device, Action, Object, Data = Analizar_argumentos()

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

    if Action == "02":
        #-----------------------------------------------------
        #--  Action: Leer el puerto
        #--  Devuelve el puerto y otros argumentos enviados como parametros
        #-----------------------------------------------------
        print("aqui va el codigo")
        Trama = s.readline()
        print("(%s)" % str(Trama))
        s.close()
        #-- leer el puerto
    elif Action == "03":
        Trama = "Esta seria la trama en hexadecimal"
        s.write(Trama)
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