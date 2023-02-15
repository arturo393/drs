#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# dmu_check_rs485.py  Ejemplo de manejo del puerto serie desde python utilizando la
# libreria multiplataforma pyserial.py (http://pyserial.sf.net)
#
#  Se envia una cadena por el puerto serie y se muestra lo que se recibe
#  Se puede especificar por la linea de comandos el puerto serie a
#  a emplear
#
#  (C)2022 Arturo Veras (arturo@sigma-telecom.com)
#
#
#  LICENCIA GPL
# -----------------------------------------------------------------------------

import cmd
import dis
import sys
import getopt
import serial
from crccheck.crc import Crc16Xmodem
import argparse
import check_rs485 as rs485
import os
#import dru_discovery as discovery
import requests,json
import time

OK =  0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

# --------------------------------
# -- Imprimir mensaje de ayuda
# --------------------------------
def help():
    sys.stderr.write("""Uso: check_portserial [opciones]
    Ejemplo de uso del puerto serie en Python

    opciones:
    -lwul, --port   Puerto serie a leer o escribir Ej. /dev/ttyS0
    -a, --action  ACTION: query ; set
    -d, --device  dmu, dru
    -x, --dmuDevice1  INTERFACE: ID de PA o DSP, Ej. F8, F9, FA, etc
    -y, --dmuDevice2  Device: DRU ID number, Ej. 80, E7, 41, etc
    -n, --cmdNumber  CMDNUMBER: Comando a enviar
    -l, --cmdBodyLenght  tamano del cuerpo en bytes, 1, 2.
    -c, --cmdDat CMDDATA: dato a escribir
    -i, --druId DRU ID number Ej. 0x11-0x16 / 0x21-0x26 / 0x31-36 / 0x41-46
    """)

def analizar_argumentos():
    
# -----------------------------------------------------
# --  Analizar los argumentos pasados por el usuario
# --  Devuelve el puerto y otros argumentos enviados como parametros
# -----------------------------------------------------
    # Construct the argument parser
    ap = argparse.ArgumentParser()
    # Add the arguments to the parser
    #ap.add_argument("-h", "--help", required=False,  help="help")
    ap.add_argument("-hlwu","--highLevelWarningUplink",  required=False,help="highLevelWarningUplink es requerido", default=200)
    ap.add_argument("-hlcu","--highLevelCriticalUplink", required=False,help="highLevelCriticalUplink es requerido", default=200)
    ap.add_argument("-hlwd","--highLevelWarningDownlink",  required=False,help="highLevelWarningDownlink es requerido", default=200)
    ap.add_argument("-hlcd","--highLevelCriticalDownlink", required=False,help="highLevelCriticalDownlink es requerido", default=200)

    try:
        args = vars(ap.parse_args())
    except getopt.GetoptError as e:
        # print help information and exit:
        print(e.msg)
        help()
        sys.exit(1)

    HighLevelWarningUL = int(args['highLevelWarningUplink'])
    HighLevelCriticalUL = int(args['highLevelCriticalUplink'])
    HighLevelWarningDL = int(args['highLevelWarningDownlink'])
    HighLevelCriticalDL = int(args['highLevelCriticalDownlink'])
    
    return  HighLevelWarningUL,  HighLevelCriticalUL,  HighLevelWarningDL, HighLevelCriticalDL
# ----------------------
#   MAIN
# ----------------------
def main():

    # -- Analizar los argumentos pasados por el usuario
    hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl  = analizar_argumentos()
    queries = getQueries()
    
    start_time = time.time()
    response_time = 0

    serial = rs485.setSerial('/dev/ttyS0',19200)
    replies = rs485.writeSerialQueries(queries,serial)
    messages =  list(zip(queries,replies))
    parameters = getParametersFromDmuMessages(messages)
    parameters = getParametersFromDmuReplies(queries, replies)
    
    response_time = time.time() - start_time
    parameters["rt"] = str(response_time)
    alarm = get_alarm_from_dict(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameters)
    parameter_html_table = create_table(parameters)      
    graphite = get_graphite_str(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameters)

    sys.stderr.write(alarm+parameter_html_table+"|"+graphite)

    if( alarm != ""):
        sys.exit(1)
    else:
        sys.exit(0)

def getQueries():
    frame_list  = list()
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','f8','01','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','f9','01','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','fa','01','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','fb','01','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','f3','00','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','ef','00','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','b9','00','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','81','00','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','36','00','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','42','00','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','9a','00','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','91','00','00','00'))
    return frame_list

def get_alarm_from_dict(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameter_dict):
    if(parameter_dict['dlOutputPower'] != '-'):
        dlPower = float(parameter_dict['dlOutputPower'])
    else:
        dlPower = -200
    if(parameter_dict['ulInputPower'] != '-'):
        ulPower = float(parameter_dict['ulInputPower'])
    else:
        ulPower = -200

    alarm =""
    if dlPower >= hl_critical_dl:
        alarm +="<h3><font color=\"#ff5566\">Downlink Power Level Critical "
        alarm += parameter_dict['dlOutputPower']
        alarm += " [dBm]!</font></h3>"
    elif dlPower >= hl_warning_dl:
        alarm +="<h3><font color=\"#ffaa44\">Downlink Power Level Warning "
        alarm += parameter_dict['dlOutputPower']
        alarm += "[dBm]</font></h3>"

    if ulPower > 0:
        alarm +=""         
    elif ulPower >= hl_critical_ul:
        alarm +="<h3><font color=\"#ff5566\">Uplink Power Level Critical " 
        alarm += parameter_dict['ulInputPower']
        alarm +="[dBm]!</font></h3>"      
    elif ulPower >= hl_warning_ul:
        alarm +="<h3><font color=\"#ffaa44\">Uplink Power Level Warning " 
        alarm += parameter_dict['ulInputPower']
        alarm += "[dBm]</font></h3>"


    return alarm

def get_graphite_str(hlwul, hlcul, hlwdl, hlcdl, parameter_dict):
    rt = parameter_dict['rt']
    
    rt_str  ="RT="+rt
    rt_str +=";"+str(1000)
    rt_str +=";"+str(2000)

    dl_str ="Downlink="+parameter_dict['dlOutputPower']
    dl_str +=";"+str(hlwdl)
    dl_str +=";"+str(hlcdl)
    graphite = rt_str+" "+dl_str
    return graphite

def create_table(responseDict):

    table1 = get_opt_status_table(responseDict)
    table2 = get_power_table(responseDict)
    table3 = get_channel_table(responseDict)

    table =  ""
    table += '<div class="sigma-container" >'
    table += table1+table2+table3
    table += "</div>"
    # tableport = '<div class="port-container" >'+table1+"</div>"
    # powertable = '<div class="port-container2" >'+table2+"</div>"
    # channeltable = '<div class="port-container3" >'+table3+"</div>"
    return table

def get_channel_table(responseDict):
    
    if (responseDict['workingMode'] == 'Channel Mode'):
        table3 = "<table width=80% >"
        table3 += "<thead><tr style=font-size:11px>"
        table3 += "<th width='10%'>Channel</font></th>"
        table3 += "<th width='10%'>Status</font></th>"
        table3 += "<th width='40%'>UpLink [Mhz]</font></th>"
        table3 += "<th width='40%'>Downlink [Mhz]</font></th>"
        table3 += "</tr></thead><tbody>"
        for i in range(1,17):
            channel = str(i)
            table3 +="<tr align=\"center\" style=font-size:11px>"
            table3 +="<td>"+channel+"</td>"
            table3 +="<td>"+responseDict["channel"+str(channel)+"Status"]+"</td>"
            table3 +="<td>"+responseDict["channel"+str(channel)+"ulFreq"]+"</td>"
            table3 +="<td>"+responseDict["channel"+str(channel)+"dlFreq"]+"</td>"
            table3 +="</tr>"
    else:        
        table3 = "<table width=80%>"
        table3 += "<thead><tr style=font-size:12px>"
        table3 += "<th width='40%'>Status</font></th>"
        table3 += "<th width='10%'>Bandwidth [Mhz]</font></th>"
        table3 += "<th width='40%'>UpLink [Mhz]</font></th>"
        table3 += "<th width='40%'>Downlink [Mhz]</font></th>"
        table3 += "</tr></thead><tbody>"
        table3 +="<tr align=\"center\" style=font-size:12px>"    
        table3 +="<td>"+responseDict['workingMode']+"</td>"
        
        table3 +="<td>"+responseDict['Bandwidth']+"</td>"
        table3 +="<td>"+responseDict['Uplink Start Frequency']+"</td>"
        table3 +="<td>"+responseDict['Downlink Start Frequency']+"</td>"
        
        
        table3 +="</tr>"

    table3 +="</tbody></table>"
    return table3

def get_power_table(responseDict):


    table2 = "<table width=250>"
    table2 += "<thead>"
    table2 += "<tr  align=\"center\" style=font-size:12px>"
    table2 += "<th width='12%'>Link</font></th>"
    table2 += "<th width='33%'>Power</font> </th>"
    table2 += "<th width='35%'>Attenuation</font></th>"
    table2 += "</tr>"
    table2 += "</thead>"
    table2 += "<tbody>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>Uplink</td><td>"+responseDict['ulInputPower']+" [dBm]</td><td>"+responseDict['ulAtt']+" [dB]</td></tr>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>Downlink</td><td>"+responseDict['dlOutputPower']+" [dBm]</td><td>"+responseDict['dlAtt']+" [dB]</td></tr>"
    table2+="</tbody></table>"
    return table2

def get_opt_status_table(responseDict):
    table1 = "<table width=280>"
    table1 += "<thead>"
    table1 += "<tr align=\"center\" style=font-size:12px>"
    table1 += "<th width='12%'>Port</font></th>"
    table1 += "<th width='22%'>Activation Status</font></th>"
    table1 += "<th width='22%'>Connected Remotes</font></th>"
    table1 += "<th width='20%'>Transmission Status</font></th>"
    table1 += "</tr>"
    table1 += "</thead>"
    table1 +="<tbody>"

    for i in range(1,5):
        opt = str(i) 
        table1 +="<tr align=\"center\" style=font-size:12px>" 
        table1 +="<td>opt"+opt+"</td>" 
        table1 +="<td>"+responseDict['opt'+opt+'ActivationStatus']+"</td>" 
        table1 +="<td>"+responseDict['opt'+opt+'ConnectedRemotes']+"</td>"
        table1 +="<td>"+responseDict['opt'+opt+'TransmissionStatus']+"</td>"
        table1 +="</tr>"

    table1 +="</tbody>"
    table1 +="</table>"
    return table1

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

def updateParametersWithDmuDataReply(parameters, reply):
    reply_data = extractDmuReplyData(reply)
    reply_data = bytearray(reply_data).hex()
    dmuReplyDecode(parameters, reply_data)

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
    dlPower = rs485.s16(hex_as_int)/256
    if dlPower >= 0 or dlPower < -110 or dlPower >= 31 :
        dlPower = "-"
    else:
        dlPower = round(dlPower,2)

    parameter_dict['dlOutputPower'] = str(dlPower)
    
    hexInvertido = hex_validated_frame[0+4:2+4]+ hex_validated_frame[2+4:4+4]
    hexInvertido2 = hex_validated_frame[2+4:4+4] + hex_validated_frame[0+4:2+4]
    hex_as_int = int(hexInvertido, 16)
    hex_as_int2 = int(hexInvertido2, 16)
    ulPower = rs485.s16(hex_as_int)/256

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
          
          downlinkFrequency = int(byteInvertido, 16)
              
          dl_start  ,up_start ,bandwidth ,downlink , uplink = rs485.get_start_freq_and_diff(downlinkFrequency)
          downlink = str(downlink).ljust(8,"0")
          uplink = str(uplink).ljust(8,"0")

          parameter["channel"+str(channel)+"ulFreq"] = downlink
          parameter["channel"+str(channel)+"dlFreq"] = uplink
          parameter["Uplink Start Frequency"] = up_start
          parameter["Downlink Start Frequency"] = dl_start
          parameter["Bandwidth"] = bandwidth

          channel += 1
          i += 8
        except:
          print("Dato recibido es desconocido ")

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


def hasDmuReplyError(reply):
    if rs485.hasReplyError(reply,"00"):
        return 1
    return 0

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
    


if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN