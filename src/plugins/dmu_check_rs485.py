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
    parameters = rs485.getParametersFromDmuMessages(messages)
    parameters = rs485.getParametersFromDmuReplies(queries, replies)
    
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
    table += '<div class="sigma-container">'
    table += table1+table2+table3
    table += "</div>"
    return table

def get_channel_table(responseDict):
    
    if (responseDict['workingMode'] == 'Channel Mode'):
        table3 = "<table width=40%>"
        table3 += "<thead><tr style=font-size:11px>"
        table3 += "<th width='10%'><font color=\"#046c94\">Channel</font></th>"
        table3 += "<th width='10%'><font color=\"#046c94\">Status</font></th>"
        table3 += "<th width='40%'><font color=\"#046c94\">UpLink Frequency</font></th>"
        table3 += "<th width='40%'><font color=\"#046c94\">Downlink Frequency</font></th>"
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
        table3 = "<table width=40%>"
        table3 += "<thead><tr style=font-size:11px>"
        table3 += "<th width='30%'><font color=\"#046c94\">Status</font></th>"
        table3 += "<th width='10%'><font color=\"#046c94\">Bandwidth</font></th>"
        table3 += "<th width='30%'><font color=\"#046c94\">UpLink Frequency</font></th>"
        table3 += "<th width='30%'><font color=\"#046c94\">Downlink Frequency</font></th>"
        table3 += "</tr></thead><tbody>"
        table3 +="<tr align=\"center\" style=font-size:11px>"    
        table3 +="<td>"+responseDict['workingMode']+"</td>"
        table3 +="<td>3[MHz]</td>"
        table3 +="<td>417[MHz]</td>"
        table3 +="<td>427[MHz]</td>"
        table3 +="</tr>"

    table3 +="</tbody></table>"
    return table3

def get_power_table(responseDict):


    table2 = "<table width=250>"
    table2 += "<thead>"
    table2 += "<tr  align=\"center\" style=font-size:12px>"
    table2 += "<th width='12%'><font color=\"#046c94\">Link</font></th>"
    table2 += "<th width='33%'><font color=\"#046c94\">Power</font> </th>"
    table2 += "<th width='35%'><font color=\"#046c94\">Attenuation</font></th>"
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
    table1 += "<th width='12%'><font color=\"#046c94\">Port</font></th>"
    table1 += "<th width='22%'><font color=\"#046c94\">Activation Status</font></th>"
    table1 += "<th width='22%'><font color=\"#046c94\">Connected Remotes</font></th>"
    table1 += "<th width='22%'><font color=\"#046c94\">Transmission Status</font></th>"
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

if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN

