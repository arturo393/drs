#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# dru_check_rs485.py  Ejemplo de manejo del puerto serie desde python utilizando la
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

from shutil import ExecError
import sys
import getopt
from crccheck.crc import Crc16Xmodem
import argparse
import check_rs485 as rs485
import time
import binascii
import logging

path = "/home/sigmadev/"
logging.basicConfig(format='%(asctime)s %(message)s',filename=path+"dru_check_rs485.log", level=logging.DEBUG)

OK =  0
WARNING = 17
CRITICAL = 2
UNKNOWN = 3

MINIMUM_FRAME_SIZE = 20
DRU_MULTIPLE_CMD_LENGTH = 5

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

    """)
# ----------------------
#   MAIN
# ----------------------
def main():

    args = analizar_argumentos()    
    queries = setRs485CmdFrames(args)
    query_id = args['opt']+args['dru'] 

    serial = rs485.setSerial('/dev/ttyS1', 9600)
    reply_time = time.time()
    replies = rs485.writeSerialQueries(queries,serial)
    reply_time = time.time()-reply_time
    messages =  list(zip(queries,replies))
    parameters = rs485.getParametersFromDruMessages(messages)
    #parameters = rs485.getParametersFromDruReplies(queries, replies, query_id)
        
    parameters["rt"] = str(round(reply_time,2))
    alarm = get_alarm_from_dict(args, parameters)
    table = create_table(parameters)    
    graphite = get_graphite_str(args, parameters)
    logging.debug("RU"+query_id+" "+graphite)
    sys.stderr.write(alarm+table+"|"+graphite)
    if( alarm != ""):
        sys.exit(1)
    else:
        sys.exit(0)



# -----------------------------------------------------
# --  Analizar los argumentos pasados por el usuario
# --  Devuelve el puerto y otros argumentos enviados como parametros
# -----------------------------------------------------

def analizar_argumentos():

    # Construct the argument parser
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    #ap.add_argument("-h", "--help", required=False,  help="help")
    ap.add_argument("-d", "--dru", required=True, help="dru es requerido", default="")
    ap.add_argument("-o", "--opt", required=True,help="opt es requerido", default="")
    ap.add_argument("-s", "--sn", required=False, help="sn es requerido", default="")
    ap.add_argument("-m", "--mac", required=False,help="mac es requerido", default="")
    ap.add_argument("-hlwu","--highLevelWarningUL",  required=False,help="highLevelWarning es requerido", default=200)
    ap.add_argument("-hlcu","--highLevelCriticalUL", required=False,help="highLevelCritical es requerido", default=200)
    ap.add_argument("-hlwd","--highLevelWarningDL",  required=False,help="highLevelWarning es requerido", default=200)
    ap.add_argument("-hlcd","--highLevelCriticalDL", required=False,help="highLevelCritical es requerido", default=200)
    ap.add_argument("-hltw","--highLevelWarningTemperature",  required=False,help="highLevelWarningTemperature es requerido", default=200)
    ap.add_argument("-hltc","--highLevelCriticalTemperature", required=False,help="highLevelCriticalTemperature es requerido", default=200)
    
    try:
        args = vars(ap.parse_args())
    except getopt.GetoptError as e:
        # print help information and exit:
        print(e.msg)
        help()
        sys.exit(1)


    dru = str(args['dru'])
    opt = str(args['opt'])
    sn = str(args['sn'])
    mac = str(args['mac']) 
    hl_warning_ul = int(args['highLevelWarningUL'])
    hl_critical_ul = int(args['highLevelCriticalUL'])
    hl_warning_dl = int(args['highLevelWarningDL'])
    hl_critical_dl = int(args['highLevelCriticalDL'])
    hl_warning_temperature = int(args['highLevelWarningTemperature'])
    hl_critical_temperature = int(args['highLevelCriticalTemperature'])
    if opt == "" :
        sys.stderr.write("CRITICAL - opt es obligatorio")
        sys.exit(2)
    elif dru == "":
        sys.stderr.write("CRITICAL - dru es obligatorio")
        sys.exit(2)
    elif mac == "" :
        sys.stderr.write("CRITICAL - mac es obligatorio")
        sys.exit(2)
    elif sn == "":
        sys.stderr.write("CRITICAL - sn es obligatorio")
        sys.exit(2)
    return args


def setRs485CmdFrames(args):
    frame_list = list()
    sn,sn_action = get_sn_str_hex(args)
    mac,mac_action = get_mac_str(args)

    # -- Armando la trama
    #def obtener_trama(Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId):
    frame_list.append(rs485.obtener_trama('set'  ,'dru','00','00','094C0B'+mac+'170500'+sn,'22','00',args['opt']+args['dru']))
    frame_list.append(rs485.obtener_trama('query','dru','00','00','04010500040305000406050004250500044004000441040004EF0B0005160A0000','23','00', args['opt']+args['dru']))
    frame_list.append(rs485.obtener_trama('query','dru','00','00','0510040000051104000005120400000513040000051404000005150400000516040000051704000005180400000519040000051A040000051B040000051C040000051D040000051E040000051F040000','52','00',args['opt']+args['dru']))
    frame_list.append(rs485.obtener_trama('query','dru','00','00','07180A0000000007190A00000000071A0A00000000071B0A00000000','1e','00',args['opt']+args['dru']))
    return frame_list

def get_mac_str(args):
    mac_str =''
    if 'mac' in args:
        mac_str = args['mac']
        action = 'set'
    else:
        while len(mac_str)<9:
            mac_str +='0'
        action = 'query'
    return mac_str,action

def get_sn_str_hex(args):
    sn_str_hex = ''
    if 'sn' in args:
        sn_str = args['sn']            
        sn_bytearray = bytearray(sn_str,'ascii')
        sn_str_hex = bytearray(sn_bytearray).hex()
        while len(sn_str_hex)<40:
            sn_str_hex +='0'
        action = 'set'
    else:
        while len(sn_str_hex)<40:
            sn_str_hex +='0'
        action = 'query'
    return sn_str_hex,action

def get_graphite_str(args, parameter_dict):

    hl_warning_uplink = int(args['highLevelWarningUL'])
    hl_critical_uplink = int(args['highLevelCriticalUL'])
    hl_warning_downlink = int(args['highLevelWarningDL'])
    hl_critical_downlink = int(args['highLevelCriticalDL'])
    hl_warning_temperature = int(args['highLevelWarningTemperature'])
    hl_critical_temperature = int(args['highLevelCriticalTemperature'])
    dlPower = parameter_dict['dlOutputPower']
    ulPower = parameter_dict['ulInputPower']
    temperature = parameter_dict['paTemperature']
    
    if(dlPower == 0.0):
        dlPowerStr = "-"
    else:
        dlPowerStr = str(dlPower)

    pa_temperature ="Temperature="+parameter_dict['paTemperature']
    pa_temperature+=";"+str(hl_warning_temperature)
    pa_temperature+=";"+str(hl_critical_temperature)
    dlPower ="Downlink="+parameter_dict['dlOutputPower']
    dlPower+=";"+str(hl_warning_downlink)
    dlPower+=";"+str(hl_critical_downlink)
    vswr  ="VSWR="+parameter_dict['vswr']
    ulPower ="Uplink="+parameter_dict['ulInputPower']
    ulPower+=";"+str(hl_warning_uplink)
    ulPower+=";"+str(hl_critical_uplink)
    rt = "RT="+ parameter_dict['rt']+";1000;2000"
    
    
    graphite =rt+" "+ pa_temperature+" "+dlPower+" "+vswr+" "+ulPower
    return graphite

def get_alarm_from_dict(args, parameter_dict):
    
    hl_warning_uplink = int(args['highLevelWarningUL'])
    hl_critical_uplink = int(args['highLevelCriticalUL'])
    hl_warning_downlink = int(args['highLevelWarningDL'])
    hl_critical_downlink = int(args['highLevelCriticalDL'])
    hl_warning_temperature = int(args['highLevelWarningTemperature'])
    hl_critical_temperature = int(args['highLevelCriticalTemperature'])


    if(parameter_dict['dlOutputPower'] != '-'):
        dlPower = float(parameter_dict['dlOutputPower'])
    else:
        dlPower = -200
    if(parameter_dict['ulInputPower'] != '-'):
        ulPower = float(parameter_dict['ulInputPower'])
    else:
        ulPower = -200
    if(parameter_dict['paTemperature'] != '-'):
        paTemperature = float(parameter_dict['paTemperature'])
    else:
        paTemperature = -200

    alarm =""
    

    if dlPower >= hl_critical_downlink:
        alarm +="<h3><font color=\"#ff5566\">Downlink Power Level Critical "
        alarm += parameter_dict['dlOutputPower']
        alarm += " [dBn]!</font></h3>"
    
    
    elif dlPower >= hl_warning_downlink:
        alarm +="<h3><font color=\"#ffaa44\">Downlink Power Level Warning "
        alarm += parameter_dict['dlOutputPower']
        alarm += "[dBm]</font></h3>"
            
    if ulPower >= hl_critical_uplink:
        alarm +="<h3><font color=\"#ff5566\">Uplink Power Level Critical " 
        alarm +=parameter_dict['ulInputPower']
        alarm +="[dBm]!</font></h3>"  

    elif ulPower >= hl_warning_uplink:
        alarm +="<h3><font color=\"#ffaa44\">Uplink Power Level Warning " 
        alarm += parameter_dict['ulInputPower']
        alarm +="[dBm]</font></h3>"


    if paTemperature >= hl_critical_temperature:
        alarm +="<h3><font color=\"#ff5566\">Temperature Level Critical "
        alarm += parameter_dict['paTemperature']
        alarm += " [°C]]!</font></h3>"

    elif paTemperature >= hl_warning_temperature:
        alarm +="<h3><font color=\"#ffaa44\">Temperature Level Warning "
        alarm += parameter_dict['paTemperature']
        alarm += " [°C]]!</font></h3>"

    return alarm

def create_table(parameter_dic):
    table1 = get_power_att_table(parameter_dic)
    table2 = get_vswr_temperature_table(parameter_dic)
    table3 = get_channel_freq_table(parameter_dic)
    
    table =  ""
    table += '<div class="sigma-container">'
    table += table2+table1+table3
    table += "</div>"
    tableportdru = '<div class="dru-container" >'+table1+"</div>"
    powertabledru = '<div class="dru-container2" >'+table2+"</div>"
    channeltabledru = '<div class="dru-container3" >'+table3+"</div>"
    return table

    

def get_channel_freq_table(parameter_dic):
    table3 = "<table width=90%>"
    table3 += "<thead><tr style=font-size:10px>"
    table3 += "<th width='10%'>Channel</font></th>"
    table3 += "<th width='10%'>Status</font></th>"
    table3 += "<th width='40%'>UpLink Frequency [Mhz]</font></th>"
    table3 += "<th width='40%'>Downlink Frequency [Mhz]</font></th>"
    table3 += "</tr></thead><tbody>"

    if (parameter_dic['workingMode'] == 'Channel Mode'):
        table3 = "<table width=100%>"
        table3 += "<thead><tr style=font-size:10px>"
        table3 += "<th width='5%'>Channel</font></th>"
        table3 += "<th width='5%'>Status</font></th>"
        table3 += "<th width='50%'>UpLink [Mhz]</font></th>"
        table3 += "<th width='50%'>Downlink [Mhz]</font></th>"
        table3 += "</tr></thead><tbody>"
        for i in range(1,17):
            channel = str(i)
            table3 +="<tr align=\"center\" style=font-size:11px>"
            table3 +="<td>"+channel+"</td>"
            table3 +="<td>"+parameter_dic["channel"+str(channel)+"Status"]+"</td>"
            table3 +="<td>"+parameter_dic["channel"+str(channel)+"ulFreq"]+"</td>"
            table3 +="<td>"+parameter_dic["channel"+str(channel)+"dlFreq"]+"</td>"
            table3 +="</tr>"
    else:        
        table3 = "<table width=90%>"
        table3 += "<thead><tr style=font-size:10px>"
        table3 += "<th width='30%'>Status</font></th>"
        table3 += "<th width='10%'>Bandwidth</font></th>"
        table3 += "<th width='30%'>UpLink [Mhz]</font></th>"
        table3 += "<th width='30%'>Downlink [Mhz]</font></th>"
        table3 += "</tr></thead><tbody>"
        table3 +="<tr align=\"center\" style=font-size:10px>"    
        table3 +="<td>"+parameter_dic['workingMode']+"</td>"
        table3 +="<td>"+parameter_dic['Bandwidth']+"</td>"
        table3 +="<td>"+parameter_dic['Uplink Start Frequency']+"</td>"
        table3 +="<td>"+parameter_dic['Downlink Start Frequency']+"</td>"
        table3 +="</tr>"

    table3+="</tbody></table>"
    return table3

def get_vswr_temperature_table(parameter_dic):
    table2  = "<table width=90%>"
    table2 += "<thead>"
    table2 += "<tr  style=font-size:12px>"
    table2 += "<th width='40%'>Temperature</font></th>"
    table2 += "<th width='40%'>VSWR</font></th>"
    table2 += "</tr>"
    table2 += "</thead>"
    table2 += "<tbody>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>"+parameter_dic['paTemperature']+" [°C]</td><td>"+parameter_dic['vswr']+"</td></tr>"
    table2 +="</tbody></table>"
    return table2

def get_power_att_table(parameter_dic):


    table1  = "<table width=90%>"
    table1 += "<thead>"
    table1 += "<tr  align=\"center\" style=font-size:12px>"
    table1 += "<th width='30%'>Link</font></th>"
    table1 += "<th width='35%'>Power</font> </th>"
    table1 += "<th width='35%'>Attenuation</font></th>"
    table1 += "</tr>"
    table1 += "</thead>"
    table1 += "<tbody>"
    table1 += "<tr align=\"center\" style=font-size:12px><td>Uplink</td><td>"+parameter_dic['ulInputPower']+" [dBm]</td><td>"+parameter_dic['ulAtt']+" [dB]</td></tr>"
    table1 += "<tr align=\"center\" style=font-size:12px><td>Downlink</td><td>"+parameter_dic['dlOutputPower']+" [dBm]</td><td>"+parameter_dic['dlAtt']+" [dB]</td></tr>"
    table1 +="</tbody></table>"
    return table1

if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN

