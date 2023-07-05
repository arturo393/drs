#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# check_rs485.py  Ejemplo de manejo del puerto serie desde python utilizando la
# libreria multiplataforma pyserial.py (http://pyserial.sf.net)
#
#  Se envia una cadena por el puerto serie y se muestra lo que se recibe
#  Se puede especificar por la linea de comandos el puerto serie a
#  a emplear
#
#  (C)2022 Guillermo Gonzalez (ggonzalez@itaum.com) creador
#          
#
#  LICENCIA GPL
# -----------------------------------------------------------------------------

from pickle import FALSE, TRUE
import sys
import getopt
import serial
from crccheck.crc import Crc16Xmodem
import argparse
import os
import time
import binascii
import logging

path = "/var/log/icinga2/"
filename = "check_rs485.log"
try:
    logging.basicConfig(format='%(asctime)s %(message)s',filename=path+filename, level=logging.DEBUG)
except Exception as e:
    logging.basicConfig(format='%(asctime)s %(message)s',filename=path+filename, level=logging.DEBUG)
    os.chmod(path+filename, 0o777)  
      
# --------------------------------
# -- Declaracion de constantes
# --------------------------------
OK =  0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

C_HEADER = '7E'
C_DATA_TYPE = '00'
C_RESPONSE_FLAG = '00'
C_END = '7E'
C_UNKNOWN2BYTE01 = '0101'
C_UNKNOWN2BYTE02 = '0100'
C_STATUS2BYTE01 = '0301'
C_UNKNOWN1BYTE = '01'
C_TXRXS_80 = '80'
C_TXRXS_FF = 'FF'
C_TYPE_QUERY = '02'
C_TYPE_SET = '03'
C_RETURN = '7E'
#C_RETURN = ''
C_SITE_NUMBER = '00000000'

MINIMUM_DRU_FRAME_SIZE = 20
DRU_MULTIPLE_CMD_LENGTH = 5
DRU_SINGLE_CMD_LENGTH = 4

dl_frec_min = 4270000
dl_frec_max = 4300000
workbandwith_vhf = 15
workbandwith_uhf = 3
dl_vhf_frec_min = 1450000
dl_vhf_frec_max = 1700000

dataDMU = {
    "F8" : "opt1",
    "F9" : "opt2",
    "FA" : "opt3",
    "FB" : "opt4",
    "9A" : ['Connected','Disconnected','Transsmision normal','Transsmision failure'],
    "F3" : "[dBm]",
    "42" : ['ON', 'OFF'],
    "81" : ["Channel Mode", "WideBand Mode"]
}

dataDRU = {
    "0300" : { "default": "Unknown Device", 4: "Fiber optic remote unit"},
    "0400" : " Device Mode",
    "0600" : " Device Channel number",
    "210B" : " RU ID",
    "0201" : "Remote ",
    "0105" : { "unidad": " [°C]", "variable" : "Temperature", "name" : "Power Amplifier Temperature"},
    "0305" : { "unidad": " [dBm]", "variable" : "Power", "name" : "Downlink Output Power" }, 
    "0605" : { "unidad": " ", "variable" : "VSWR", "name" : "Downlink VSWR" },
    "2505" : { "unidad": " [dBm]", "variable" : "Power", "name" : "Uplink Input Power" },
    "0104" : { "default" : "Unknown", 0: "RF Power OFF" , 1: "RF Power On" },
    "4004" : " [dB]",
    "4104" : " [dB]",
    "EF0B" : { "default": "Unknown", 2: "WideBand Mode", 3: "Channel Mode"},
    "180A" : " MHz",
    "190A" : " MHz",
    "1A0A" : " MHz",
    "1B0A" : " MHz",
    "0102" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "0602" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "0F02" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "1002" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "1102" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "1202" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "1302" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "1402" : { "default": "Unknown", 0: "Disable", 1: "Enable"},
    "0103" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "0603" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "0E03" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "0F03" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "1003" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "1103" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "1203" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "1303" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},
    "1403" : { "default": "Unknown", 0: "Alarm OFF", 1: "Alarm ON"},  
    "5004" : " V",
    "5104" : " &ordm;C",
    "5304" : " [dBm]",
    "5404" : " [dBm]",
    "5504" : " [dBm]",
    "5604" : " [dBm]",
    "270A" : { "default": "Unknown", 1: "180 [s]", 3: "60 [s]", 9: "20 [s]"},
    "E00B" : " [dBm]",
    "E10B" : " [dBm]",
    "E20B" : " [dBm]",
    "E30B" : " [dBm]",
    "E40B" : " [dBm]",
    "E50B" : " [dBm]",
    "E40B" : " [dBm]",
    "E50B" : " [dBm]"
    
}


# --------------------------------
# -- Imprimir mensaje de ayuda
# --------------------------------
def help():
    sys.stderr.write("""Uso: check_portserial [opciones]
    Ejemplo de uso del puerto serie en Python

    opciones:
    -p, --port   Puerto serie a leer o escribir Ej. /dev/ttyS0
    -a, --action  ACTION: query ; set 
    -d, --device  dmu, dru
    -x, --dmuDevice1  INTERFACE: ID de PA o DSP, Ej. F8, F9, FA, etc
    -y, --dmuDevice2  Device: DRU ID number, Ej. 80, E7, 41, etc
    -n, --cmdNumber  CMDNUMBER: Comando a enviar
    -l, --cmdBodyLenght  tamano del cuerpo en bytes, 1, 2.
    -c, --cmdDat CMDDATA: dato a escribir 
    -i, --druId DRU ID number Ej. 0x11-0x16 / 0x21-0x26 / 0x31-36 / 0x41-46 

    
    Ejemplo:
    check_portserial.py -p COM0       --> Usar el primer puerto serie (Windows)
    check_portserial.py -p /dev/ttyS0 --> Especificar el dispositivo serie (Linux) 
    
    """)
# ----------------------
#   MAIN
# ----------------------
  
def main():

    # -- Analizar los argumentos pasados por el usuario
    Port, Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId, LowLevelWarning, HighLevelWarning, LowLevelCritical, HighLevelCritical  = analizar_argumentos()

    # -- Armando la trama
    query = obtener_trama(Action, Device, DmuDevice1,
                          DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId)
    s = serial_init(Port)
    if Action == "query" or Action == "set":
        #write_serial_frame(Trama, s)
        #hexResponse = read_serial_frame(s)
        write_serial_frame(query, s)
        time.sleep(0.2)
        reply = read_serial_frame(s)
        s.close()
        data = validar_trama_respuesta(reply, Device,len(CmdNumber))
       
        if Action == 'set':
            if len(data) == 0 and Device == 'dmu':
                reply = ''.join(format(x, '02x') for x in reply)
                logging.debug("DMU Error - Can't validate data "+str(reply))
                sys.exit(CRITICAL)
            elif len(data) == 0 and Device == 'dru':
                logging.debug(
                    "DRU - Can't send a message to remote device")
                print("No Response")
                sys.exit(CRITICAL)
            else:
                if Device == 'dru':
                    a_bytearray = bytearray(data)
                    hex_string = a_bytearray.hex()
                    logging.debug("DRU OK - Reply: "+str(reply))
                    print("OK")
                    sys.exit(OK)
                if Device == 'dmu':
                    a_bytearray = bytearray(data)
                    resultHEX = a_bytearray.hex()
                    logging.debug("DMU OK - Reply: "+str(reply))
                    print("OK")
                    sys.exit(OK)

                
        elif Action == 'query':
            a_bytearray = bytearray(data)
            resultHEX = a_bytearray.hex()
            try:
                resultOK =  s8(int(resultHEX, 16))
            except:
                print("- Unknown received message")
                sys.exit(3)    
            
        if len(CmdNumber) > 4:
            hex_string = convertirMultipleRespuesta(data)
        else:   
            hex_string =  convertirRespuestaHumana(resultHEX, Device, CmdNumber,HighLevelCritical,HighLevelWarning)

        if (resultOK  >= HighLevelCritical) :
            print("CRITICAL Alert! - " + hex_string )
            sys.exit(CRITICAL)
        elif (resultOK >=  HighLevelWarning) :
            print("WARNING Alert !- " + hex_string  )
            sys.exit(WARNING)
        else:
            print("OK - " + hex_string )
            sys.exit(OK)     
    else:
        logging.debug(
            "- Invalid action  %s \n" % Action)
        sys.exit(WARNING)

def analizar_argumentos():
# -----------------------------------------------------
# --  Analizar los argumentos pasados por el usuario
# --  Devuelve el puerto y otros argumentos enviados como parametros
# -----------------------------------------------------

    # Construct the argument parser
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    #ap.add_argument("-h", "--help", required=False,  help="help")
    ap.add_argument("-p", "--port", required=True,  help="port es requerido", )
    ap.add_argument("-a", "--action", required=True,
                    help="action es requerido")
    ap.add_argument("-d", "--device", required=True,
                    help="device es requerido")
    ap.add_argument("-x", "--dmuDevice1", required=False,
                    help="dmuDevice1 es requerido", default="")
    ap.add_argument("-y", "--dmuDevice2", required=False,
                    help="dmuDevice2 es requerido", default="")
    ap.add_argument("-n", "--cmdNumber", required=True,
                    help="cmdNumber es requerido")
    ap.add_argument("-l", "--cmdBodyLenght", required=False,
                    help="cmdBodyLenght es requerido", default="")
    ap.add_argument("-c", "--cmdData", required=False,
                    help="cmdData es requerido", default="")
    ap.add_argument("-i", "--druId", required=False,
                    help="druId es requerido", default="")
    ap.add_argument("-lw", "--lowLevelWarning", required=False,
                    help="lowLevelWarning es requerido", default=0)
    ap.add_argument("-hw", "--highLevelWarning", required=False,
                    help="highLevelWarning es requerido", default=200)
    ap.add_argument("-lc", "--lowLevelCritical", required=False,
                    help="lowLevelCritical es requerido", default=0)
    ap.add_argument("-hc", "--highLevelCritical", required=False,
                    help="highLevelCritical es requerido", default=200)
                                                    
    try:
        args = vars(ap.parse_args())
    except getopt.GetoptError as e:
        # print help information and exit:
        print(e.msg)
        help()
        sys.exit(1)

    Port = str(args['port'])
    Action = str(args['action'])
    Device = str(args['device'])
    DmuDevice1 = str(args['dmuDevice1'])
    DmuDevice2 = str(args['dmuDevice2'])
    CmdNumber = str(args['cmdNumber'])
    CmdBodyLenght = str(args['cmdBodyLenght'])
    CmdData = str(args['cmdData'])
    DruId = str(args['druId'])
    LowLevelWarning = int(args['lowLevelWarning'])
    HighLevelWarning = int(args['highLevelWarning'])
    LowLevelCritical = int(args['lowLevelCritical'])
    HighLevelCritical = int(args['highLevelCritical'])

    # validamos los argumentos pasados
    if Port == "":
        sys.stderr.write("CRITICAL - El puerto es obligatorio\n")
        sys.exit(2)

    if Device == "":
        sys.stderr.write("CRITICAL - El device es obligatorio\n")
        sys.exit(2)

    if DmuDevice1 == "" and Device == 'dmu':
        sys.stderr.write(
            "CRITICAL - El dmuDevice1 es obligatorio\n")
        sys.exit(2)

    if DmuDevice2 == "" and Device == 'dmu':
        sys.stderr.write(
            "CRITICAL - El dmuDevice2 es obligatorio\n")
        sys.exit(2)

    if CmdNumber == "":
        sys.stderr.write("  CRITICAL - cmdNumber es obligatorio\n")
        sys.exit(2)

    if (CmdBodyLenght == "" and Action == 'set') or (CmdBodyLenght == "" and Device == 'dru'):
        sys.stderr.write(
            "CRITICAL - cmdBodyLenght es obligatorio")
        sys.exit(2)

    if (CmdData == "" and Action == 'set') or (CmdData == "" and Device == 'dru'):
        sys.stderr.write("CRITICAL - cmdData es obligatorio")
        sys.exit(2)

    if (DruId == "" and Device == 'dru'):
        sys.stderr.write("CRITICAL - DruId es obligatorio")
        sys.exit(2)

    return Port, Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId, LowLevelWarning, HighLevelWarning, LowLevelCritical, HighLevelCritical

def getChecksumSimple(cmd):
    """
    -Description: this fuction calculate the checksum for a given comand
    -param text: string with the data, ex device = 03 , id = 03 cmd = 0503110000
    -return: cheksum for the given command
    """
    data = bytearray.fromhex(cmd)

    crc = hex(Crc16Xmodem.calc(data))
    #print("crc: %s" % crc)

    if (len(crc) == 5):
        checksum = crc[3:5] + '0' + crc[2:3]
    else:
        checksum = crc[4:6] + crc[2:4]
    
    checksum = checksum.upper()
    return checksum

def getChecksum(cmd):
    """
    -Description: this fuction calculate the checksum for a given comand
    -param text: string with the data, ex device = 03 , id = 03 cmd = 0503110000
    -return: cheksum for the given command
    """
    data = bytearray.fromhex(cmd)

    crc = hex(Crc16Xmodem.calc(data))
    #print("crc: %s" % crc)

    if (len(crc) == 5):
        checksum = crc[3:5] + '0' + crc[2:3]
    else:
        checksum = crc[4:6] + crc[2:4]
    
    checksum = checksum.upper()
    checksum_new = checksum.replace('7E','5E7D')      
    #checksum_new = checksum.replace('5E','5E5D')      
    return checksum_new

def getChecksum2(data):
    """
    -Description: this fuction calculate the checksum for a given comand
    -param text: string with the data, ex device = 03 , id = 03 cmd = 0503110000
    -return: cheksum for the given command
    """
    
    crcdata = Crc16Xmodem.calc(data)
    crc = hex(crcdata)
    #print("crc: %s" % crc)

    if (len(crc) == 5):
        checksum = crc[3:5] + '0' + crc[2:3]
    elif (len(crc) == 4):
        checksum = crc[2:4] + '00'
    else:
        checksum = crc[4:6] + crc[2:4]
    
    checksum = checksum.upper()
    if(checksum[:2] == '7E' or checksum[2:] == '7E'):
         checksum = checksum.replace('7E','5E7D')      
    #checksum_new = checksum.replace('5E','5E5D')      
    return checksum

def buscaArray(lst, value):

    try:
       ndx = lst.index(value)
    except:
      ndx = -1

    return ndx

def formatearHex(dato):

    if dato[0:2] == '0x':
        dato_hex = dato[2:]
    else:
        dato_hex = dato

    return dato_hex

def obtener_trama(Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId):
    
# ----------------------------------------------------
# -- Armar trama de escritura o lectura
#-- (PARAMETROS)
# -- Interface: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
# -- CmdNumber: 80 = Send ; 00 = Receive
# -- CmdBodyLenght: Indentica si lee o escribe
# -- CmdData: dato a escribir <integer en hex>
# -- Crc: Byte de control
# ---------------------------------------------------

    DmuDevice1_hex = formatearHex(DmuDevice1)
    #print('DmuDevice1_hex: %s' % DmuDevice1_hex)

    DmuDevice2_hex = formatearHex(DmuDevice2)
    #print('DmuDevice2_hex: %s' % DmuDevice2_hex)

    CmdNumber_hex = formatearHex(CmdNumber)
    #print('CmdNumber_hex: %s' % CmdNumber_hex)

    #print('CmdBodyLenght: %s' % CmdBodyLenght)
    if (Device == 'dru'):
        CmdBodyLenght_hex = formatearHex(CmdBodyLenght)

        CmdData_hex = formatearHex(CmdData)
        #print('CmdData_hex: %s' % CmdData_hex)

        DruId_hex = formatearHex(DruId)
        #print('DruId_hex: %s' % DruId_hex)

        try:
            cant_bytes = int(CmdBodyLenght_hex, 16)
            #print('cant_bytes: %s' % cant_bytes)
        except ValueError:
            logging.debug(
                "CRITICAL - CmdBodyLenght no tiene formato hexadecimal")
            sys.exit(2)
        tramaLengthCodeData = CmdBodyLenght_hex + CmdNumber_hex + CmdData_hex
        #print('tramaLengthCodeData: %s' % tramaLengthCodeData)
        lenTramaLengthCodeData = int(len(tramaLengthCodeData)/2)
        #print('lenTramaLengthCodeData: %s' % lenTramaLengthCodeData)
        if lenTramaLengthCodeData != cant_bytes:
            logging.debug(
                "CRITICAL - CmdBodyLenght + CmdNumber + CmdData, no corresponde a la cantidad de bytes indicados\n")
            sys.exit(2)
        if (Action == 'set'):
            MessageType = C_TYPE_SET
        else:
            MessageType = C_TYPE_QUERY

        Retunr_hex = C_RETURN

    else:

        Retunr_hex = ''
        if (Action == 'set'):
            CmdData_hex = formatearHex(CmdData)
            #print('CmdData_hex: %s' % CmdData_hex)
            CmdBodyLenght_hex = formatearHex(CmdBodyLenght)
        else:
            CmdData_hex = ''
            CmdBodyLenght_hex = '00'
    #print('CmdNumber_hex: %s' % CmdNumber_hex)

    #print('Device: %s' % Device)
    if Device == 'dru':
        if(CmdNumber_hex == 'a003'):
            cmd_string = C_STATUS2BYTE01 + C_SITE_NUMBER + DruId_hex + C_UNKNOWN2BYTE02 + C_TXRXS_80 + \
                C_UNKNOWN1BYTE + MessageType + C_TXRXS_FF + \
                CmdBodyLenght_hex + CmdNumber_hex + CmdData_hex
        else: 
            cmd_string = C_UNKNOWN2BYTE01 + C_SITE_NUMBER + DruId_hex + C_UNKNOWN2BYTE02 + C_TXRXS_80 + \
                C_UNKNOWN1BYTE + MessageType + C_TXRXS_FF + \
                CmdBodyLenght_hex + CmdNumber_hex + CmdData_hex
    elif(DmuDevice1_hex == '08'):
        cmd_string = DmuDevice1_hex + DmuDevice2_hex + \
            CmdNumber_hex + C_RESPONSE_FLAG + CmdBodyLenght_hex + CmdData_hex
        #print('La trama corta: %s' % cmd_string)
        checksum = getChecksumSimple(cmd_string)  # calcula CRC
        trama = C_HEADER + cmd_string + checksum + '7F' + Retunr_hex
        #print('Query: %s' % trama)
        return str(trama)
    else:
        cmd_string = DmuDevice1_hex + DmuDevice2_hex + C_DATA_TYPE + \
            CmdNumber_hex + C_RESPONSE_FLAG + CmdBodyLenght_hex + CmdData_hex

    #print('La trama corta: %s' % cmd_string)
    checksum = getChecksum(cmd_string)  # calcula CRC

    trama = C_HEADER + cmd_string + checksum + C_END + Retunr_hex

    #print('Query: %s' % trama)
    return str(trama)

def validar_trama_respuesta(hexResponse, Device,cmdNumberlen):
    try:
        if Device == 'dru':
            data = validateDruReply(hexResponse, cmdNumberlen)   
        else:
            data = extractDmuReplyData(hexResponse)
        return data
    except ValueError as ve:
        logging.debug("ValueError frame "+str(hexResponse)+" "+str(ve)+"\n")
        return []
        sys.exit(CRITICAL)
    except Exception as e:
        logging.debug("Exception validate frame "+str(hexResponse)+" "+str(e)+"\n")
        return []
        sys.exit(CRITICAL) 

def extractDmuReplyData(reply):
    data = list()
    index_cmd_lenght = 6
    index_cmd_number = 4
    cant_bytes_resp = int(reply[index_cmd_lenght])+1+1+1
            
    rango_i = index_cmd_number
    rango_n = rango_i + cant_bytes_resp
    for i in range(rango_i, rango_n):
            data.append(reply[i])
    return data

def hastIdReplyError(reply,query_id):
    if(query_id == '00'):
        return 0
    query_id = bytes.fromhex(query_id)
    query_id = int.from_bytes(query_id, "big")
    REPLY_ID_INDEX = 7
    reply_id = reply[REPLY_ID_INDEX]
    reply  = ''.join(format(x, '02x') for x in reply)
    if( reply_id != query_id):
        logging.debug("RU"+str(hex(query_id))+" Error - reply id "+str(hex(reply_id))+"is not the same "+str(reply))
        return 1
    return 0
    
def hasReplyError(reply,query_id):
    if query_id == "00":
        query_id = "DMU"
    else:
        query_id = "RU"+query_id
   
    if (reply == None or reply == "" or reply == " "  or len(reply) == 0 ):
        logging.debug(query_id+" Error - Blank Response ")
        return 1
    try:
        reply_crc, calculated_crc = getReplyCrc(reply)
    except Exception as e:
        logging.debug(query_id+" - " +str(e)+" "+str(reply))
        return 1
    if(reply_crc != calculated_crc):
        reply_crc  = ''.join(format(x, '02x') for x in reply_crc)
        calculated_crc  = ''.join(format(x, '02x') for x in calculated_crc)
        reply  = ''.join(format(x, '02x') for x in reply)             
        logging.debug(query_id+" Error - CRC reply: "+str(reply_crc)+"  CRC calculated: " +str(calculated_crc) + " " + str(reply))
        return 1
    return 0

def hasSizeReplyError(reply):
    if(reply == '7e' or len(reply) < MINIMUM_DRU_FRAME_SIZE ):
        reply = binascii.hexlify(bytearray(reply))
        logging.debug(" Frame Size Error - frame is not valid: "+ str(reply)+"\n")
        return 1

def hasDruReplyError(reply,query_id):
    if hasReplyError(reply,query_id):
        return 1
    if hasSizeReplyError(reply):
        return 1
    if hastIdReplyError(reply,query_id):
        return 1
    return 0

def hasDmuReplyError(reply):
    if hasReplyError(reply,"00"):
        return 1
    return 0

def getReplyCrc(reply):
    reply_size = len(reply)
    reply_crc = reply[reply_size-3:reply_size-1]
    reply_clean = reply[1:reply_size-3]                  
    calculated_crc = getChecksum2(reply_clean)
    calculated_crc = bytearray.fromhex(calculated_crc)
    return reply_crc,calculated_crc

def validateDruReply(reply,cmdNumberlen):
    
    reply_size = len(reply)
           
    reply_crc = reply[reply_size-3:reply_size-1]
    reply_clean = reply[1:reply_size-3]                  
    calculated_crc = getChecksum2(reply_clean)
    calculated_crc = bytearray.fromhex(calculated_crc)

    if(reply_crc == calculated_crc or reply_crc == b'\x00\x00' ):
        reply_data = extractDruReplyData(reply, cmdNumberlen)
    return reply_data

def extractDruReplyData(reply, cmdNumberlen):
    
    reply_data_lenght_index = 14  # Para equipos remotos  de la trama
    reply_data_lenght = int(reply[reply_data_lenght_index])  
    if(cmdNumberlen == DRU_MULTIPLE_CMD_LENGTH):
        reply_data_start_index =  reply_data_lenght_index+1
        reply_data_end_index = reply_data_start_index + reply_data_lenght - 1
    else: 
        reply_data_start_index = reply_data_lenght_index + 3
        reply_data_end_index = reply_data_start_index + reply_data_lenght - 3
            
    reply_data = list()
    for i in range(reply_data_start_index, reply_data_end_index):
        reply_data.append(reply[i])
    return reply_data

def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

def s8(byte):
    if byte > 127:
        return (256-byte) * (-1)
    else:
        return byte

def convertirRespuestaHumana(Result, Device, CmdNumber,high_level_critical,high_level_warning):
    try:
        CmdNumber = CmdNumber.upper()
        Device = Device.lower()
        if Device=='dmu' and (CmdNumber=='F8' or CmdNumber=='F9' or CmdNumber=='FA' or CmdNumber=='FB'):
            Value =  int(Result, 16)
            if(Value >8):
                logging.debug("- Wrong Remotes value: " + str(Value))
                sys.exit(1)  
            else :
                 Result = str(Value) + " Remotes Discovered | value=" + str(Value) 
            
                    
        elif  Device=='dmu' and CmdNumber=='91':
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>Port</th><th width='15%'>Status</th><th width='70%'>&nbsp;</th></tr></thead><tbody>"
            if (Result[0:2] == '00'):
                Table += "<tr><td>OPT1</td><td>ON</td><td>&nbsp;</td></tr>"                
            else:
                Table += "<tr><td>OPT1</td><td>OFF</td><td>&nbsp;</td></tr>"                 

            if (Result[2:4] == '00'):
                Table += "<tr><td>OPT2</td><td>ON</td><td>&nbsp;</td></tr>"                
            else:
                Table += "<tr><td>OPT2</td><td>OFF</td><td>&nbsp;</td></tr>"                 

            if (Result[4:6] == '00'):
                Table += "<tr><td>OPT3</td><td>ON</td><td>&nbsp;</td></tr>"                
            else: 
                Table += "<tr><td>OPT3</td><td>OFF</td><td>&nbsp;</td></tr>"                
            
            if (Result[6:8] == '00'):
                Table += "<tr><td>OPT4</td><td>ON</td><td>&nbsp;</td></tr>"                
            else:                 
                Table += "<tr><td>OPT4</td><td>OFF</td><td>&nbsp;</td></tr>"   
            
            Table +=   "</tbody></table>" 
            Result = Table
        
        elif (Device=='dmu' and CmdNumber=='9A'):
            hex_as_int = int(Result, 16)
            hex_as_binary = bin(hex_as_int)
            padded_binary = hex_as_binary[2:].zfill(8)
            opt=1
            temp = []
            for bit in reversed(padded_binary):  
                if (bit=='0' and opt<=4):
                    temp.append('Connected ') 
                elif (bit=='1' and opt<=4):
                    temp.append('Disconnected ')
                elif (bit=='0' and opt>4):
                    temp.append('Normal')
                elif (bit=='1' and opt>4):
                    temp.append('Failure')
                opt=opt+1          
            
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>Port</th><th width='20%'>Status</th><th width='20%'>Transmission</th><th>&nbsp;</th></tr></thead><tbody>"
            Table += "<tr><td>OPT1</td><td>" + temp[0]  + "</td><td>" + temp[4] + "</td><td>&nbsp;</td></tr>"
            Table += "<tr><td>OPT2</td><td>" + temp[1]  + "</td><td>" + temp[5] + "</td><td>&nbsp;</td></tr>"
            Table += "<tr><td>OPT3</td><td>" + temp[2]  + "</td><td>" + temp[6] + "</td><td>&nbsp;</td></tr>"
            Table += "<tr><td>OPT4</td><td>" + temp[3]  + "</td><td>" + temp[7] + "</td><td>&nbsp;</td></tr>"
            Table += "</tbody></table>" 
            Result = Table

        elif (Device=='dmu' and CmdNumber=='F3'):    
            hexInvertido = Result[2:4] + Result[0:2]
            hex_as_int = int(hexInvertido, 16)
            decSigned = s16(hex_as_int)
            rbm = decSigned/256
            formato ='{:,.2f}'.format(rbm).replace(",", "@").replace(".", ",").replace("@", ".")
            #Result = formato + " [dBm] | power=" + str(rbm)
            
            hexInvertido = Result[0+4:2+4]+ Result[2+4:4+4]
            #print(Result,hexInvertido)
            hex_as_int = int(hexInvertido, 16)
            ulPower = s16(hex_as_int)/256
            ulPowerStr = str(round(ulPower,2))
            #ulPowerStr = "-"
            
            hexInvertido = Result[2:4] + Result[0:2]
            #print(Result,hexInvertido)
            hex_as_int = int(hexInvertido, 16)
            dlPower = s16(hex_as_int)/256
            dlPowerStr = str(round(dlPower,2))

            ul_output = "Uplink Power "+ulPowerStr+" [dBm]" 
            dl_output = "Downlink Power "+dlPowerStr+" [dBm]"
            output = ul_output+", "+dl_output
          
            table = "<table width=250>"
            table += "<thead>"
            table += "<tr  align=\"center\" style=font-size:12px>"
            table += "<th width='12%'><\">Link</font></th>"
            table += "<th width='33%'><\">Power</font> </th>"
            table += "</tr>"
            table += "</thead>"
            table += "<tbody>"
            table += "<tr align=\"center\" style=font-size:12px><td>Uplink</td><td>"+ulPowerStr+" [dBm]</td></tr>"
            table += "<tr align=\"center\" style=font-size:12px><td>Downlink</td><td>"+dlPowerStr+" [dBm]</td></tr>"
            table +="</tbody></table>"
            
            uplinkg_graphite  ="Uplink="+ulPowerStr
            downlink_graphite ="Downlink="+dlPowerStr
            graphite = uplinkg_graphite+" "+downlink_graphite

            Result = output+"|"+graphite

        elif (Device=='dmu' and CmdNumber=='42'):    
            i = 0            
            channel = 1
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>CHANNEL</th><th width='15%'>VALUE</th><th width='70%'>&nbsp;</th></tr></thead><tbody>"
            while channel <= 16 and i < len(Result):
                hex_as_int = int(Result[i:i+2], 16)
                if hex_as_int == 0:                    
                    Table += "<tr><td>"+ str(channel).zfill(2) + "</td><td>ON</td><td>&nbsp;</td></tr>"
                else:                    
                    Table += "<tr><td>"+ str(channel).zfill(2) + "</td><td>OFF</td><td>&nbsp;</td></tr>"
                i += 2
                channel += 1
            Table +=   "</tbody></table>"            
            Result = Table

        elif (Device=='dmu' and CmdNumber=='36'): 
            channel = 1
            i = 0            
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='12%'>Channel</th><th width='13%'>Subchannel<th width='25%'>Uplink Frecuency</th><th width='50%'>Downlink Frecuency</th></tr></thead><tbody>"
            while channel <= 16:
                byte = Result[i:i+8]
                byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2]             
                hex_as_int = int(byteInvertido, 16)                
                texto = frequencyDictionary[hex_as_int]
                Table += "<tr><td>" + str(channel).zfill(2) + "</td><td>" +  texto[0:3] + "</td><td>" + texto[4:22-6+2]  + "</td><td>" + texto[23:40-6+2] + "</td></tr>"
                channel += 1
                i += 8
            Table +=   "</tbody></table>"                
            Result = Table
        
        elif (Device=='dmu' and CmdNumber=='81'):
            tmp = ''
            if Result == '03':
                tmp = 'Channel Mode ' 
            elif Result == '02':
                tmp = 'WideBand Mode '
            else:
                tmp = 'Unknown '
            Result = tmp     
        
        elif (Device=='dmu' and CmdNumber=='EF'):
            byte01toInt = int(Result[0:2], 16)/4
            byte02toInt = int(Result[2:4], 16)/4
            valor1 = '{:,.2f}'.format(byte01toInt).replace(",", "@").replace(".", ",").replace("@", ".")
            valor2 = '{:,.2f}'.format(byte02toInt).replace(",", "@").replace(".", ",").replace("@", ".")
            Result = valor1 + " Uplink ATT [dB] - " + valor2 + " Downlink ATT [dB] "
        
        elif (Device=='dmu' and CmdNumber=='84'):
            tmp = ''
            if Result == '01':
                tmp = 'On ' 
            elif Result == '00':
                tmp = 'Off'
            else:
                tmp = 'Unknown '
            Result = tmp       
        #convirtiendo hex to decimal

        elif (Device=='dru' and (CmdNumber=='0300' or CmdNumber=='0104' or CmdNumber=='EF0B' or CmdNumber=='0102'
             or CmdNumber=='0602' or CmdNumber=="0F02" or CmdNumber=="1002" or CmdNumber=="1102" or CmdNumber=="1202" 
             or CmdNumber=="1302"  or CmdNumber=="1402" or CmdNumber=="0103" or CmdNumber=="0603" or CmdNumber=="0E03"
             or CmdNumber=="0F03" or CmdNumber=="1003" or CmdNumber=="1103" or CmdNumber=="1203" or CmdNumber=="1303" 
             or CmdNumber=="1403" or CmdNumber=="270A")):
             try:
                  list = dataDRU[CmdNumber]
                  tmp = list[int(Result, 16)]
             except:    
                  tmp = list['default']
             Result = tmp
        
        
        #convirtiendo hex to decimal
        elif (Device=='dru' and (CmdNumber=='0600' or CmdNumber=='210B' or CmdNumber=='4004' or CmdNumber=='4104'
              or CmdNumber=='5004'  or CmdNumber=='5104'  or CmdNumber=='5304'  or CmdNumber=='5404'  or CmdNumber=='5504'
              or CmdNumber=='5604' or CmdNumber=='E00B' or CmdNumber=='E10B' or CmdNumber=='E20B' or CmdNumber=='E30B'
              or CmdNumber=='E40B'  or CmdNumber=='E50B')):                
            tmp =  str(int(Result, 16)) + dataDRU[CmdNumber]
            Result = tmp
        
        #convirtiendo hex to Ascii  
        elif (Device=='dru' and (CmdNumber=='0400' or CmdNumber=='0500'  or CmdNumber=="0A00") ):
             tmp =  bytearray.fromhex(Result).decode()
             Result = tmp
        
        #mostrar en hexadecimal  
        elif (Device=='dru' and (CmdNumber=='0201' ) ):
             tmp =  dataDRU[CmdNumber] + Result 
             Result = tmp

        #convirtiendo hex to decimal con signo
        elif (Device=='dru' and (CmdNumber=='0105' or CmdNumber=='0305' or CmdNumber=='2505')):
             list = dataDRU[CmdNumber]
             decSigned = s8(int(Result, 16))
             formato = '{:,.2f}'.format(decSigned).replace(",", "@").replace(".", ",").replace("@", ".")
             tmp =  str(formato) +  list['unidad'] + "|" + list['variable'] + "=" + str(decSigned)+";"+str(high_level_warning)+";"+str(high_level_critical)
             Result = tmp 

        elif (Device=='dru' and (CmdNumber=='0605' )):
             list = dataDRU[CmdNumber]
             decSigned = s8(int(Result, 16))/10
             formato = '{:,.2f}'.format(decSigned).replace(",", "@").replace(".", ",").replace("@", ".")
             tmp =  str(formato) +  list['unidad'] + "|" + list['variable'] + "=" + str(decSigned)+";"+str(high_level_warning)+";"+str(high_level_critical)
             Result = tmp 
        
        elif (Device=='dru' and (CmdNumber=='160A' )):
            hex = Result
            byte1 = hex[0:2]
            byte2 = hex[2:4]

            # Code to convert hex to binary
            res1 = "{0:08b}".format(int(byte1, 16))
            res2 = "{0:08b}".format(int(byte2, 16))
            binario = res1 + res2
            channel = 0            
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>OPT</th><th width='15%'>VALUE</th><th width='70%'>&nbsp;</th></tr></thead><tbody>"
            for i  in binario:
                channel += 1
                if (i == '1' ):                    
                    Table += "<tr><td>" + str(channel).zfill(2) + "</td><td>ON</td><td>&nbsp;</td></tr>"                             
                else:
                    Table += "<tr><td>" + str(channel).zfill(2) + "</td><td>OFF</td><td>&nbsp;</td></tr>"                    
            Table +=   "</tbody></table>"
            Result = hex+" "+Table

        elif (Device=='dru' and (CmdNumber=='180A' or CmdNumber=='190A' or CmdNumber=='1A0A' or CmdNumber=='1B0A')):  
            byte = Result
            byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2]             
            hex_as_int = int(byteInvertido, 16)            
            frecuency = hex_as_int / 10000
            formato = '{:,.4f}'.format(frecuency).replace(",", "@").replace(".", ",").replace("@", ".")
            Result = str(formato) + dataDRU[CmdNumber]         
        
        elif (Device=='dru' and (CmdNumber=='1004' or CmdNumber=='1104' or CmdNumber=='1204' or CmdNumber=='1304'
             or CmdNumber=='1404' or CmdNumber=='1504' or CmdNumber=='1604' or CmdNumber=='1704' or CmdNumber=='1804'
             or CmdNumber=='1904' or CmdNumber=='1A04' or CmdNumber=='1B04' or CmdNumber=='1C04' or CmdNumber=='1D04'
             or CmdNumber=='1E04' or CmdNumber=='1F04')):                                      
            byte0 = int(Result[0:2], 16)            
            channel = 4270000 + (125 * byte0)
            Result = 'CH ' + frequencyDictionary[channel]
        elif CmdNumber =='4C0B':
            logging.debug(Result)
        #    sys.exit(0)  
        return Result
    except Exception as e:
        logging.debug("- Failed to read message from device: " + Result)
        sys.exit(1)    
        
def convertirMultipleRespuesta(data):
    i = 0
    j = 0
    temp = list()
    dataResult = list()
    isWriting = False
    for i in range(len(data)):
        
        if isWriting == False:
            dataLen = data[i]
            isWriting = True
    
        if j<dataLen-1:
            temp.append(data[i+1])    
            j = j+1
        else:
            isWriting = False
            j = 0
            a_bytearray = bytearray(temp)
            resultHEX = a_bytearray.hex()
            dataResult.append(resultHEX)
            temp.clear() 
              
    paTemp = 0
    dlOutputPw = 0
    dlVswr = 0
    ulInputPw = 0      
    graphite = ""
    table =""      
    for data in dataResult:
        cmdNumber = data[:4]
        cmdValue = data[4:]
        if(cmdNumber =='0105' or cmdNumber =='0305' or cmdNumber =='2505' or cmdNumber =='0605'):
             parameter = dataDRU[cmdNumber]
             if cmdNumber == '0605':
                 decSigned = s16(int(cmdValue,16))/10
             else: 
                 decSigned = s16(int(cmdValue, 16))
             value = '{:,.2f}'.format(decSigned).replace(",", "@").replace(".", ",").replace("@", ".")
             name = parameter['name']
             unit = parameter['unidad']
             variable = parameter['variable']
             graphite = graphite +variable+unit+ "=" + str(decSigned)+";"
             table = table + "<tr style=font-size:15px><td>"+name+"</td><td>"+value+unit+"</td></tr>"
    
    Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
    Table += "<thead><tr><th width='15%'></th><th width='20%'></th></tr></thead><tbody>"
    Table +=  table
    Table += "</tbody></table>" 
    Table += "|" + graphite
    return Table

def setSerial(port, baudrate):
    for times in range(3):
        try:
            s = serial.Serial(port, baudrate)
            s.timeout = 0.1
            s.exclusive = True

        except serial.SerialException as e:
            logging.debug(
                "WARNING - "+str(times)+" "+str(e)+" "+str(port))
            #sys.stderr.write(str(e))
            time.sleep(1)
    return s
    logging.debug(
        "CRITICAL - No Connection to "+str(port))
    sys.stderr.write("CRITICAL - No Connection to "+str(port))
    sys.exit(CRITICAL)

def read_serial_frame(s):
    hexadecimal_string = ''
    rcvHexArray = list()
    isDataReady = False
    rcvcount = 0
    while not isDataReady:
        try:
            Response = s.read()
        except serial.SerialException as e:
            logging.debug(str(e))
            return bytearray()
        rcvHex = Response.hex()
        if(rcvcount == 0 and rcvHex == '7e'):
            rcvHexArray.append(rcvHex)
            hexadecimal_string = hexadecimal_string + rcvHex
            rcvcount = rcvcount + 1
        elif(rcvcount > 0 and rcvHexArray[0] == '7e' and (rcvcount == 1 and rcvHex == '7e') is not True):
            rcvHexArray.append(rcvHex)
            hexadecimal_string = hexadecimal_string + rcvHex
            rcvcount = rcvcount + 1
            if(rcvHex == '7e' or rcvHex == '7f'):
                isDataReady = True
        elif rcvHex == '':
            return ""
            
    s.reset_input_buffer()
    hexResponse = bytearray.fromhex(hexadecimal_string)
    return hexResponse

def write_serial_frame(Trama, s):
    cmd_bytes = bytearray.fromhex(Trama)
    hex_byte = ''
    for cmd_byte in cmd_bytes:
        hex_byte = ("{0:02x}".format(cmd_byte))
        s.write(bytes.fromhex(hex_byte))
    s.flush()
    
def serial_init(Port):
    for times in range(3):
        try:
            if Port == '/dev/ttyS0':      
                baudrate = 19200
            else:
                baudrate = 9600
            s = serial.Serial(Port, baudrate)
            s.timeout = 0.1
        except UnboundLocalError as e:
            logging.debug(
                "CRITICAL - "+str(e)+" "+str(Port))
            sys.stderr.write("CRITICAL - "+str(e)+" "+str(Port))
            sys.exit(CRITICAL)
        except serial.SerialException as e:
            logging.debug(
                "WARNING - "+str(times)+" "+str(e)+" "+str(Port))
            time.sleep(1)
    return s

def writeSerialQueries(queries,serial):
    replies = list()
    response_time = 0.0
    for query in queries:
        start_time = time.time()
        write_serial_frame(query, serial)
        reply = read_serial_frame(serial)
        replies.append(reply)
        tmp = time.time() - start_time
        logging.debug("time - "+str(round(tmp,2)))                
        if tmp > response_time:
            response_time = tmp
        time.sleep(response_time)
    serial.close()
    return replies

def druReplyDecode(parameters,reply_data):
    
    cmd_number = reply_data[:4]
    cmd_value = reply_data[4:]
    
    if cmd_number =='0105':
        temperature = s8(int(cmd_value,16))
        parameters['paTemperature'] = str(temperature)
                                                                                                                
    elif cmd_number == '0305':
        dl_power = s8(int(cmd_value, 16))

        if(int(dl_power) == 0 or int(dl_power) >= 31):
            parameters['dlOutputPower'] ="-"
        else:
            parameters['dlOutputPower'] = str(dl_power)
        
    elif cmd_number == '2505':
        ul_power = s8(int(cmd_value, 16))
        parameters['ulInputPower'] = str(ul_power)
                
    elif cmd_number == '0605':
        vswr = s8(int(cmd_value, 16))/10
        parameters['vswr'] = str(round(vswr,2))
        
    elif cmd_number == '4004':
        ul_att = (int(cmd_value, 16))
        parameters['ulAtt'] = str(ul_att)  
                                
    elif cmd_number == '4104':
        dl_att = (int(cmd_value, 16))
        parameters['dlAtt'] = str(dl_att)
        
    elif cmd_number == 'ef0b':
        working_mode = (int(cmd_value, 16))

        if working_mode == 2:
            parameters['workingMode'] = "WideBand Mode"
        elif working_mode == 3:
            parameters['workingMode'] = "Channel Mode"
        else:
            parameters['workingMode'] = "Unknown"
    elif cmd_number == "180a":
          byte = cmd_value[0:0+8]
          byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2] 
          up_start_freq = (int(byteInvertido,16))
          parameters["Uplink Start Frequency"] =str(up_start_freq/10000)
          
    elif cmd_number == "190a":
          byte = cmd_value[0:0+8]
          byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2] 
          dl_start_freq = (int(byteInvertido,16))
          parameters["Downlink Start Frequency"] = str(dl_start_freq/10000)
          
          
    elif cmd_number == "1a0a":
          byte = cmd_value[0:0+8]
          byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2] 
          work_bandwith = (int(byteInvertido,16))
          parameters["Work Bandwidth"] = str(work_bandwith/10000)
          
    elif cmd_number == "1b0a":
          byte = cmd_value[0:0+8]
          byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2] 
          channel_bandwith = (int(byteInvertido,16))
          parameters["Channel Bandwidth"] = str(channel_bandwith/10000)
          
                    
    elif (cmd_number == '1004' or cmd_number == '1104' or cmd_number == '1204'
        or cmd_number == '1304' or cmd_number == '1404' or cmd_number == '1504'
        or cmd_number == '1604' or cmd_number == '1704' or cmd_number == '1804'
        or cmd_number == '1904' or cmd_number == '1a04' or cmd_number == '1b04'
        or cmd_number == '1c04' or cmd_number == '1d04' or cmd_number == '1e04'
        or cmd_number == '1f04'):
        

        if(parameters["Downlink Start Frequency"] != '-'):
            byte0 = int(cmd_value[0:2], 16)   
            ch_number = int(cmd_number[1],16)+1
            float_dl = (float(parameters["Downlink Start Frequency"]))
            dlStartFreq=float_dl*10000
            hex_as_int = dlStartFreq + (125 * byte0)
            hexdl,hexup,dl_start,up_start,bandwidth= get_downlink_uplink_freq(hex_as_int)
            parameters["channel"+str(ch_number)+"ulFreq"] = hexup
            parameters["channel"+str(ch_number)+"dlFreq"] = hexdl

            
        
        


    
    elif cmd_number == '160a':
        byte2 = cmd_value[0:2]
        byte1 = cmd_value[2:4]
        res1 = "{0:08b}".format(int(byte1, 16))
        res2 = "{0:08b}".format(int(byte2, 16))
        binario = res1 + res2
        hex_as_int = 0            
        for i  in binario:
            hex_as_int += 1                
            if (i == '1' ):  
                parameters["channel"+str(hex_as_int)+"Status"] = "ON"                      
            else:
                parameters["channel"+str(hex_as_int)+"Status"] = "OFF"  
    elif cmd_number =='4c0b':
        mac = cmd_value
        parameters['mac'] = mac
    elif cmd_number =='0500':
        sn = bytearray.fromhex(reply_data)
        sn = [i for i in sn if i != 0]
        del sn[0]
        a_bytearray = bytearray(sn)
        resultHEX = a_bytearray.hex()
        sn = bytearray.fromhex(resultHEX).decode()
        parameters['sn'] = sn
 
def dmuReplyDecode(parameters, reply_data):
    
    cmd_number = reply_data[:2]
    cmd_value = reply_data[6:]
    
    if cmd_number=='f8':
        parameters['opt1ConnectedRemotes'] = cmd_value
    elif cmd_number=='f9':
        parameters['opt2ConnectedRemotes'] = cmd_value
    elif cmd_number=='fa':
        parameters['opt3ConnectedRemotes'] = cmd_value
    elif cmd_number=='fb':
        parameters['opt4ConnectedRemotes'] = cmd_value
    elif cmd_number=='91':
        set_opt_status_dict(parameters, cmd_value)
    elif cmd_number=='9a':
        set_opt_working_status(parameters, cmd_value)
    elif cmd_number=='f3':
        set_power_dict(parameters, cmd_value)
    elif cmd_number=='42':
        set_channel_status_dict(parameters, cmd_value)
    elif cmd_number=='36':
        set_channel_freq_dict(parameters, cmd_value)
    elif cmd_number=='81':
        set_working_mode_dict(parameters, cmd_value)   
    elif cmd_number=='ef':
        set_power_att_dict(parameters, cmd_value)

def splitMultipleReplyData(reply_data):
    i = 0
    j = 0
    temp = list()
    dataResult = list()
    isWriting = False

    try:
        for i in range(0,len(reply_data)-1):
            if isWriting == False:
                dataLen = reply_data[i]
                isWriting = True

            if j<dataLen-1:
                temp.append(reply_data[i+1])
                j = j+1
            else:
                isWriting = False
                j = 0
                a_bytearray = bytearray(temp)
                resultHEX = a_bytearray.hex()
                dataResult.append(resultHEX)
                temp.clear()
        return dataResult
    except Exception as e:
        print(str(e))
        return []
     
def newBlankDruParameter():
    parameters = dict()
    
    if('dlOutputPower' not in parameters):
        parameters['dlOutputPower'] = '-'
    if('ulInputPower' not in parameters):
        parameters['ulInputPower'] = '-'
    if('paTemperature' not in parameters):
        parameters['paTemperature'] = '-'
    if('dlAtt' not in parameters):
        parameters['dlAtt'] = '-'
    if('ulAtt' not in parameters):
        parameters['ulAtt'] = '-'
    if('vswr' not in parameters):
        parameters['vswr'] = '-'
    if('workingMode' not in parameters):
        parameters['workingMode'] = '-'
    if('mac' not in parameters):
        parameters['mac'] = '-'
    if('sn' not in parameters):
        parameters['sn'] = '-'
    if("Uplink Start Frequency"not in parameters):
        parameters["Uplink Start Frequency"]= '-'
    if("Downlink Start Frequency"not in parameters):
        parameters["Downlink Start Frequency"]= '-'
    parameters["Work Bandwidth"]= '-'
    for i in range(1,17):
        channel = str(i)
        if("channel"+str(channel)+"Status" not in parameters):
            parameters["channel"+str(channel)+"Status"] = '-'
        if("channel"+str(channel)+"ulFreq" not in parameters):
            parameters["channel"+str(channel)+"ulFreq"] = '-'    
        if("channel"+str(channel)+"dlFreq" not in parameters):
            parameters["channel"+str(channel)+"dlFreq"] = '-'
    
    return parameters

def newBlankDmuParameter():
    parameters = dict()
    parameters['opt1ConnectedRemotes'] = "-"
    parameters['opt2ConnectedRemotes'] = "-"
    parameters['opt3ConnectedRemotes'] = "-"
    parameters['opt4ConnectedRemotes'] = "-"
    parameters['opt1ConnectionStatus'] = "-"
    parameters['opt2ConnectionStatus'] = "-"
    parameters['opt3ConnectionStatus'] = "-"
    parameters['opt4ConnectionStatus'] = "-"
    parameters['opt1TransmissionStatus'] = "-"
    parameters['opt2TransmissionStatus'] = "-"
    parameters['opt3TransmissionStatus'] = "-"
    parameters['opt4TransmissionStatus'] = "-"
    parameters['dlOutputPower'] = "-"
    parameters['ulInputPower'] ="-"
    parameters['ulAtt'] = "-"
    parameters['dlAtt'] = "-"
    parameters['workingMode'] = "-"
    parameters['opt1ActivationStatus'] = '-'
    parameters['opt2ActivationStatus'] = '-'
    parameters['opt3ActivationStatus'] = '-'
    parameters['opt4ActivationStatus'] = '-'
    parameters["Uplink Start Frequency"]= '-'
    parameters["Downlink Start Frequency"]= '-'
    parameters['Bandwidth']= '-'

    channel = 1
    while channel <= 16:
      parameters["channel"+str(channel)+"Status"] = "-"
      parameters["channel"+str(channel)+"ulFreq"] = "-"
      parameters["channel"+str(channel)+"dlFreq"] = "-"
      channel += 1
    return parameters

def set_opt_status_dict(parameter_dict, hex_validated_frame):
    if (hex_validated_frame[0:2] == '00'):
        parameter_dict['opt1ActivationStatus'] = 'ON'
    else:
        parameter_dict['opt1ActivationStatus'] = 'OFF'

    if (hex_validated_frame[2:4] == '00'):
        parameter_dict['opt2ActivationStatus'] = 'ON'
    else:
        parameter_dict['opt2ActivationStatus'] = 'OFF'

    if (hex_validated_frame[4:6] == '00'):
        parameter_dict['opt3ActivationStatus'] = 'ON'
    else:
        parameter_dict['opt3ActivationStatus'] = 'OFF'

    if (hex_validated_frame[6:8] == '00'):
        parameter_dict['opt4ActivationStatus'] = 'ON'
    else:
        parameter_dict['opt4ActivationStatus'] = 'OFF'

def set_opt_working_status(parameter_dict, hex_validated_frame):
    hex_as_int = int(hex_validated_frame, 16)
    hex_as_binary = bin(hex_as_int)
    padded_binary = hex_as_binary[2:].zfill(8)
    opt=1
    temp = []
    for bit in reversed(padded_binary):
        if (bit=='0' and opt<=4):
            temp.append('Connected ')
        elif (bit=='1' and opt<=4):
            temp.append('Disconnected ')
        elif (bit=='0' and opt>4):
            temp.append('Normal')
        elif (bit=='1' and opt>4):
            temp.append('Failure')
        opt=opt+1

    parameter_dict['opt1ConnectionStatus'] = temp[0]
    parameter_dict['opt2ConnectionStatus'] = temp[1]
    parameter_dict['opt3ConnectionStatus'] = temp[2]
    parameter_dict['opt4ConnectionStatus'] = temp[3]
    parameter_dict['opt1TransmissionStatus'] = temp[4]
    parameter_dict['opt2TransmissionStatus'] = temp[5]
    parameter_dict['opt3TransmissionStatus'] = temp[6]
    parameter_dict['opt4TransmissionStatus'] = temp[7]

def set_power_dict(parameter_dict, hex_validated_frame):
    hexInvertido = hex_validated_frame[2:4] + hex_validated_frame[0:2]
    hex_as_int = int(hexInvertido, 16)
    dlPower = s16(hex_as_int)/256
    if dlPower >= 0 or dlPower < -110 or dlPower >= 31 :
        dlPower = "-"
    else:
        dlPower = round(dlPower,2)

    parameter_dict['dlOutputPower'] = str(dlPower)
    
    hexInvertido = hex_validated_frame[0+4:2+4]+ hex_validated_frame[2+4:4+4]
    hexInvertido2 = hex_validated_frame[2+4:4+4] + hex_validated_frame[0+4:2+4]
    hex_as_int = int(hexInvertido, 16)
    hex_as_int2 = int(hexInvertido2, 16)
    ulPower = s16(hex_as_int)/256

    if ulPower >= 0 or ulPower < -110 or ulPower >= 31 :
        ulPower = "-"
    else:
        ulPower = round(ulPower,2)

    parameter_dict['ulInputPower'] = str(ulPower)

def set_channel_status_dict(parameter_dict, hex_validated_frame):
    i = 0
    channel = 1
    while channel <= 16 and i < len(hex_validated_frame):
        hex_as_int = int(hex_validated_frame[i:i+2], 16)
        if hex_as_int == 0:
            parameter_dict["channel"+str(channel)+"Status"] = "ON"
        else:
            parameter_dict["channel"+str(channel)+"Status"] = "OFF"
        i += 2
        channel += 1

def set_channel_freq_dict(parameter, hex_validated_frame):
    channel = 1
    i = 0
    while channel <= 16:
        try:
          byte = hex_validated_frame[i:i+8]
          byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2]
          
          hex_as_int = int(byteInvertido, 16)
              
          hexdl, hexup ,dl_start  ,up_start ,bandwidth = get_downlink_uplink_freq(hex_as_int)    
          parameter["channel"+str(channel)+"ulFreq"] = hexup
          parameter["channel"+str(channel)+"dlFreq"] = hexdl
          parameter["Uplink Start Frequency"] = up_start
          parameter["Downlink Start Frequency"] = dl_start
          parameter["Bandwidth"] = bandwidth

          channel += 1
          i += 8
        except:
          print("Dato recibido es desconocido ")

def get_downlink_uplink_freq(hex_as_int):
    dl_up_dif = int()

    
    if(hex_as_int >= dl_frec_min and hex_as_int <= dl_frec_max):
        dl_up_dif = 10
        dl_start = dl_frec_min/10000
        up_start = dl_start-dl_up_dif
        bandwith = workbandwith_uhf
    elif(hex_as_int >= dl_vhf_frec_min and hex_as_int <= dl_vhf_frec_max):
        dl_up_dif = (dl_vhf_frec_min-dl_vhf_frec_max)/10000
        dl_start = dl_vhf_frec_min/10000
        up_start = dl_start-dl_up_dif
        bandwith = workbandwith_vhf
    else:
        dl_up_dif = 0
        dl_start = 0
        up_start = 0
        bandwith = 0

    hextodlmhz = hex_as_int/10000
    hextoupmhz =  hextodlmhz - dl_up_dif
    dl_start = str(dl_start)
    up_start = str(up_start)
    bandwith = str(bandwith)
   
    hexdl = str(hextodlmhz).ljust(8,"0")
    hexup = str(hextoupmhz).ljust(8,"0")
    
    return hexdl,hexup,dl_start,up_start,bandwith
        

def set_power_att_dict(parameter_dict, hex_validated_frame):
    byte01toInt = int(hex_validated_frame[0:2], 16)/4
    byte02toInt = int(hex_validated_frame[2:4], 16)/4
    valor1 = '{:,.2f}'.format(byte01toInt).replace(",", "@").replace(".", ",").replace("@", ".")
    valor2 = '{:,.2f}'.format(byte02toInt).replace(",", "@").replace(".", ",").replace("@", ".")
    parameter_dict['ulAtt'] = valor1
    parameter_dict['dlAtt'] = valor2

def set_working_mode_dict(parameter_dict, hex_validated_frame):
    try:
        #print(hex_validated_frame)
      if hex_validated_frame == '03':
          parameter_dict['workingMode'] = 'Channel Mode'
      elif hex_validated_frame == '02':
          parameter_dict['workingMode'] = 'WideBand Mode'
      else:
          parameter_dict['workingMode'] = 'Unknown Mode'
    except:
        print("WARNING - Dato recibido es desconocido ")
        print(hex_validated_frame)

def updateParametersWithDmuDataReply(parameters, reply):
    reply_data = extractDmuReplyData(reply)
    reply_data = bytearray(reply_data).hex()
    dmuReplyDecode(parameters, reply_data)
    
def getParametersFromDmuMessages(messages):
    parameters = newBlankDmuParameter()
    reply_errors_count = 0
    for message in messages:
        query = message[0]
        reply = message[1]
        logging.debug("DMU Query: "+str(query).lower())
        reply_temp = ''.join(format(x, '02x') for x in reply)
        logging.debug("DMU Reply: "+str(reply_temp))
        if hasDmuReplyError(reply):
            reply_errors_count +=1
        else:
            updateParametersWithDmuDataReply(parameters, reply)
            
    queries_count = len(messages)
    if reply_errors_count == queries_count:
        sys.stderr.write("No response")
        sys.exit(CRITICAL)
    return parameters
    
def getParametersFromDmuReplies(queries, replies):
    parameters = newBlankDmuParameter()
    reply_errors_count = 0
    for reply in replies:
        if hasDmuReplyError(reply):
            reply_errors_count +=1
        else:
            updateParametersWithDmuDataReply(parameters, reply)
            
    queries_count = len(queries)
    if reply_errors_count == queries_count:
        sys.stderr.write("No response")
        sys.exit(CRITICAL)
    return parameters

def getParametersFromDruMessages(messages):
    parameters = newBlankDruParameter()
    reply_errors_count = 0
    
    for message in messages:
        query = message[0]
        reply = message[1]
        QUERY_ID_INDEX = 14
        query_id = query[QUERY_ID_INDEX:QUERY_ID_INDEX+2]
        logging.debug("[Check] RU"+query_id+ " Query: "+str(query).lower())
        reply_temp = ''.join(format(x, '02x') for x in reply)
        logging.debug("[Check] RU"+query_id+ " Reply: "+str(reply_temp))
        if hasDruReplyError(reply,query_id):
            reply_errors_count +=1
        else:
            updateParametersWithReplyData(parameters, reply)
    
    queries_count = len(messages)
    if reply_errors_count == queries_count:
        sys.stderr.write("No response")
        sys.exit(CRITICAL)
    return parameters

def getParametersFromDruReplies(queries, replies, query_id):
    parameters = newBlankDruParameter()
    reply_errors_count = 0
    for reply in replies:
        if hasDruReplyError(reply,query_id):
            reply_errors_count +=1
        else:
            updateParametersWithReplyData(parameters, reply)
    
    queries_count = len(queries)
    if reply_errors_count == queries_count:
        sys.stderr.write("No response")
        sys.exit(CRITICAL)
    return parameters

def updateParametersWithReplyData(parameters, reply):
    
    try:
        reply_data = extractDruReplyData(reply, DRU_MULTIPLE_CMD_LENGTH)
    except Exception as e:
        logging.debug(str(e)+"- "+str(reply))
        return 1

    try:
        reply_datas = splitMultipleReplyData(reply_data)
    except Exception as e:
        logging.debug(str(e)+"-"+str(reply_data))
        return 1      
    try:
     for data in reply_datas:
        druReplyDecode(parameters, data)
    
    except Exception as e:
        logging.debug(str(e)+"- "+str(data))
        return 1
    return 0 



if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code	Status
# 0	OK
# 1	WARNING
# 2	CRITICAL
# 3	UNKNOWN

