#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# check_rs485.py  Ejemplo de manejo del puerto serie desde python utilizando la
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

from logging import CRITICAL, WARN
import sys
import getopt
import serial
from crccheck.crc import Crc16Xmodem
import argparse
import check_rs485 as rs485
import os
import dru_discovery as discovery
import requests,json

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

frequencyDictionary = {
4270000  : '000:  417,0000 MHz UL - 427,0000 MHz DL',
4270125  : '001:  417,0125 MHz UL - 427,0125 MHz DL',
4270250  : '002:  417,0250 MHz UL - 427,0250 MHz DL',
4270375  : '003:  417,0375 MHz UL - 427,0375 MHz DL',
4270500  : '004:  417,0500 MHz UL - 427,0500 MHz DL',
4270625  : '005:  417,0625 MHz UL - 427,0625 MHz DL',
4270750  : '006:  417,0750 MHz UL - 427,0750 MHz DL',
4270875  : '007:  417,0875 MHz UL - 427,0875 MHz DL',
4271000  : '008:  417,1000 MHz UL - 427,1000 MHz DL',
4271125  : '009:  417,1125 MHz UL - 427,1125 MHz DL',
4271250  : '010:  417,1250 MHz UL - 427,1250 MHz DL',
4271375  : '011:  417,1375 MHz UL - 427,1375 MHz DL',
4271500  : '012:  417,1500 MHz UL - 427,1500 MHz DL',
4271625  : '013:  417,1625 MHz UL - 427,1625 MHz DL',
4271750  : '014:  417,1750 MHz UL - 427,1750 MHz DL',
4271875  : '015:  417,1875 MHz UL - 427,1875 MHz DL',
4272000  : '016:  417,2000 MHz UL - 427,2000 MHz DL',
4272125  : '017:  417,2125 MHz UL - 427,2125 MHz DL',
4272250  : '018:  417,2250 MHz UL - 427,2250 MHz DL',
4272375  : '019:  417,2375 MHz UL - 427,2375 MHz DL',
4272500  : '020:  417,2500 MHz UL - 427,2500 MHz DL',
4272625  : '021:  417,2625 MHz UL - 427,2625 MHz DL',
4272750  : '022:  417,2750 MHz UL - 427,2750 MHz DL',
4272875  : '023:  417,2875 MHz UL - 427,2875 MHz DL',
4273000  : '024:  417,3000 MHz UL - 427,3000 MHz DL',
4273125  : '025:  417,3125 MHz UL - 427,3125 MHz DL',
4273250  : '026:  417,3250 MHz UL - 427,3250 MHz DL',
4273375  : '027:  417,3375 MHz UL - 427,3375 MHz DL',
4273500  : '028:  417,3500 MHz UL - 427,3500 MHz DL',
4273625  : '029:  417,3625 MHz UL - 427,3625 MHz DL',
4273750  : '030:  417,3750 MHz UL - 427,3750 MHz DL',
4273875  : '031:  417,3875 MHz UL - 427,3875 MHz DL',
4274000  : '032:  417,4000 MHz UL - 427,4000 MHz DL',
4274125  : '033:  417,4125 MHz UL - 427,4125 MHz DL',
4274250  : '034:  417,4250 MHz UL - 427,4250 MHz DL',
4274375  : '035:  417,4375 MHz UL - 427,4375 MHz DL',
4274500  : '036:  417,4500 MHz UL - 427,4500 MHz DL',
4274625  : '037:  417,4625 MHz UL - 427,4625 MHz DL',
4274750  : '038:  417,4750 MHz UL - 427,4750 MHz DL',
4274875  : '039:  417,4875 MHz UL - 427,4875 MHz DL',
4275000  : '040:  417,5000 MHz UL - 427,5000 MHz DL',
4275125  : '041:  417,5125 MHz UL - 427,5125 MHz DL',
4275250  : '042:  417,5250 MHz UL - 427,5250 MHz DL',
4275375  : '043:  417,5375 MHz UL - 427,5375 MHz DL',
4275500  : '044:  417,5500 MHz UL - 427,5500 MHz DL',
4275625  : '045:  417,5625 MHz UL - 427,5625 MHz DL',
4275750  : '046:  417,5750 MHz UL - 427,5750 MHz DL',
4275875  : '047:  417,5875 MHz UL - 427,5875 MHz DL',
4276000  : '048:  417,6000 MHz UL - 427,6000 MHz DL',
4276125  : '049:  417,6125 MHz UL - 427,6125 MHz DL',
4276250  : '050:  417,6250 MHz UL - 427,6250 MHz DL',
4276375  : '051:  417,6375 MHz UL - 427,6375 MHz DL',
4276500  : '052:  417,6500 MHz UL - 427,6500 MHz DL',
4276625  : '053:  417,6625 MHz UL - 427,6625 MHz DL',
4276750  : '054:  417,6750 MHz UL - 427,6750 MHz DL',
4276875  : '055:  417,6875 MHz UL - 427,6875 MHz DL',
4277000  : '056:  417,7000 MHz UL - 427,7000 MHz DL',
4277125  : '057:  417,7125 MHz UL - 427,7125 MHz DL',
4277250  : '058:  417,7250 MHz UL - 427,7250 MHz DL',
4277375  : '059:  417,7375 MHz UL - 427,7375 MHz DL',
4277500  : '060:  417,7500 MHz UL - 427,7500 MHz DL',
4277625  : '061:  417,7625 MHz UL - 427,7625 MHz DL',
4277750  : '062:  417,7750 MHz UL - 427,7750 MHz DL',
4277875  : '063:  417,7875 MHz UL - 427,7875 MHz DL',
4278000  : '064:  417,8000 MHz UL - 427,8000 MHz DL',
4278125  : '065:  417,8125 MHz UL - 427,8125 MHz DL',
4278250  : '066:  417,8250 MHz UL - 427,8250 MHz DL',
4278375  : '067:  417,8375 MHz UL - 427,8375 MHz DL',
4278500  : '068:  417,8500 MHz UL - 427,8500 MHz DL',
4278625  : '069:  417,8625 MHz UL - 427,8625 MHz DL',
4278750  : '070:  417,8750 MHz UL - 427,8750 MHz DL',
4278875  : '071:  417,8875 MHz UL - 427,8875 MHz DL',
4279000  : '072:  417,9000 MHz UL - 427,9000 MHz DL',
4279125  : '073:  417,9125 MHz UL - 427,9125 MHz DL',
4279250  : '074:  417,9250 MHz UL - 427,9250 MHz DL',
4279375  : '075:  417,9375 MHz UL - 427,9375 MHz DL',
4279500  : '076:  417,9500 MHz UL - 427,9500 MHz DL',
4279625  : '077:  417,9625 MHz UL - 427,9625 MHz DL',
4279750  : '078:  417,9750 MHz UL - 427,9750 MHz DL',
4279875  : '079:  417,9875 MHz UL - 427,9875 MHz DL',
4280000  : '080:  418,0000 MHz UL - 428,0000 MHz DL',
4280125  : '081:  418,0125 MHz UL - 428,0125 MHz DL',
4280250  : '082:  418,0250 MHz UL - 428,0250 MHz DL',
4280375  : '083:  418,0375 MHz UL - 428,0375 MHz DL',
4280500  : '084:  418,0500 MHz UL - 428,0500 MHz DL',
4280625  : '085:  418,0625 MHz UL - 428,0625 MHz DL',
4280750  : '086:  418,0750 MHz UL - 428,0750 MHz DL',
4280875  : '087:  418,0875 MHz UL - 428,0875 MHz DL',
4281000  : '088:  418,1000 MHz UL - 428,1000 MHz DL',
4281125  : '089:  418,1125 MHz UL - 428,1125 MHz DL',
4281250  : '090:  418,1250 MHz UL - 428,1250 MHz DL',
4281375  : '091:  418,1375 MHz UL - 428,1375 MHz DL',
4281500  : '092:  418,1500 MHz UL - 428,1500 MHz DL',
4281625  : '093:  418,1625 MHz UL - 428,1625 MHz DL',
4281750  : '094:  418,1750 MHz UL - 428,1750 MHz DL',
4281875  : '095:  418,1875 MHz UL - 428,1875 MHz DL',
4282000  : '096:  418,2000 MHz UL - 428,2000 MHz DL',
4282125  : '097:  418,2125 MHz UL - 428,2125 MHz DL',
4282250  : '098:  418,2250 MHz UL - 428,2250 MHz DL',
4282375  : '099:  418,2375 MHz UL - 428,2375 MHz DL',
4282500  : '100:  418,2500 MHz UL - 428,2500 MHz DL',
4282625  : '101:  418,2625 MHz UL - 428,2625 MHz DL',
4282750  : '102:  418,2750 MHz UL - 428,2750 MHz DL',
4282875  : '103:  418,2875 MHz UL - 428,2875 MHz DL',
4283000  : '104:  418,3000 MHz UL - 428,3000 MHz DL',
4283125  : '105:  418,3125 MHz UL - 428,3125 MHz DL',
4283250  : '106:  418,3250 MHz UL - 428,3250 MHz DL',
4283375  : '107:  418,3375 MHz UL - 428,3375 MHz DL',
4283500  : '108:  418,3500 MHz UL - 428,3500 MHz DL',
4283625  : '109:  418,3625 MHz UL - 428,3625 MHz DL',
4283750  : '110:  418,3750 MHz UL - 428,3750 MHz DL',
4283875  : '111:  418,3875 MHz UL - 428,3875 MHz DL',
4284000  : '112:  418,4000 MHz UL - 428,4000 MHz DL',
4284125  : '113:  418,4125 MHz UL - 428,4125 MHz DL',
4284250  : '114:  418,4250 MHz UL - 428,4250 MHz DL',
4284375  : '115:  418,4375 MHz UL - 428,4375 MHz DL',
4284500  : '116:  418,4500 MHz UL - 428,4500 MHz DL',
4284625  : '117:  418,4625 MHz UL - 428,4625 MHz DL',
4284750  : '118:  418,4750 MHz UL - 428,4750 MHz DL',
4284875  : '119:  418,4875 MHz UL - 428,4875 MHz DL',
4285000  : '120:  418,5000 MHz UL - 428,5000 MHz DL',
4285125  : '121:  418,5125 MHz UL - 428,5125 MHz DL',
4285250  : '122:  418,5250 MHz UL - 428,5250 MHz DL',
4285375  : '123:  418,5375 MHz UL - 428,5375 MHz DL',
4285500  : '124:  418,5500 MHz UL - 428,5500 MHz DL',
4285625  : '125:  418,5625 MHz UL - 428,5625 MHz DL',
4285750  : '126:  418,5750 MHz UL - 428,5750 MHz DL',
4285875  : '127:  418,5875 MHz UL - 428,5875 MHz DL',
4286000  : '128:  418,6000 MHz UL - 428,6000 MHz DL',
4286125  : '129:  418,6125 MHz UL - 428,6125 MHz DL',
4286250  : '130:  418,6250 MHz UL - 428,6250 MHz DL',
4286375  : '131:  418,6375 MHz UL - 428,6375 MHz DL',
4286500  : '132:  418,6500 MHz UL - 428,6500 MHz DL',
4286625  : '133:  418,6625 MHz UL - 428,6625 MHz DL',
4286750  : '134:  418,6750 MHz UL - 428,6750 MHz DL',
4286875  : '135:  418,6875 MHz UL - 428,6875 MHz DL',
4287000  : '136:  418,7000 MHz UL - 428,7000 MHz DL',
4287125  : '137:  418,7125 MHz UL - 428,7125 MHz DL',
4287250  : '138:  418,7250 MHz UL - 428,7250 MHz DL',
4287375  : '139:  418,7375 MHz UL - 428,7375 MHz DL',
4287500  : '140:  418,7500 MHz UL - 428,7500 MHz DL',
4287625  : '141:  418,7625 MHz UL - 428,7625 MHz DL',
4287750  : '142:  418,7750 MHz UL - 428,7750 MHz DL',
4287875  : '143:  418,7875 MHz UL - 428,7875 MHz DL',
4288000  : '144:  418,8000 MHz UL - 428,8000 MHz DL',
4288125  : '145:  418,8125 MHz UL - 428,8125 MHz DL',
4288250  : '146:  418,8250 MHz UL - 428,8250 MHz DL',
4288375  : '147:  418,8375 MHz UL - 428,8375 MHz DL',
4288500  : '148:  418,8500 MHz UL - 428,8500 MHz DL',
4288625  : '149:  418,8625 MHz UL - 428,8625 MHz DL',
4288750  : '150:  418,8750 MHz UL - 428,8750 MHz DL',
4288875  : '151:  418,8875 MHz UL - 428,8875 MHz DL',
4289000  : '152:  418,9000 MHz UL - 428,9000 MHz DL',
4289125  : '153:  418,9125 MHz UL - 428,9125 MHz DL',
4289250  : '154:  418,9250 MHz UL - 428,9250 MHz DL',
4289375  : '155:  418,9375 MHz UL - 428,9375 MHz DL',
4289500  : '156:  418,9500 MHz UL - 428,9500 MHz DL',
4289625  : '157:  418,9625 MHz UL - 428,9625 MHz DL',
4289750  : '158:  418,9750 MHz UL - 428,9750 MHz DL',
4289875  : '159:  418,9875 MHz UL - 428,9875 MHz DL',
4290000  : '160:  419,0000 MHz UL - 429,0000 MHz DL',
4290125  : '161:  419,0125 MHz UL - 429,0125 MHz DL',
4290250  : '162:  419,0250 MHz UL - 429,0250 MHz DL',
4290375  : '163:  419,0375 MHz UL - 429,0375 MHz DL',
4290500  : '164:  419,0500 MHz UL - 429,0500 MHz DL',
4290625  : '165:  419,0625 MHz UL - 429,0625 MHz DL',
4290750  : '166:  419,0750 MHz UL - 429,0750 MHz DL',
4290875  : '167:  419,0875 MHz UL - 429,0875 MHz DL',
4291000  : '168:  419,1000 MHz UL - 429,1000 MHz DL',
4291125  : '169:  419,1125 MHz UL - 429,1125 MHz DL',
4291250  : '170:  419,1250 MHz UL - 429,1250 MHz DL',
4291375  : '171:  419,1375 MHz UL - 429,1375 MHz DL',
4291500  : '172:  419,1500 MHz UL - 429,1500 MHz DL',
4291625  : '173:  419,1625 MHz UL - 429,1625 MHz DL',
4291750  : '174:  419,1750 MHz UL - 429,1750 MHz DL',
4291875  : '175:  419,1875 MHz UL - 429,1875 MHz DL',
4292000  : '176:  419,2000 MHz UL - 429,2000 MHz DL',
4292125  : '177:  419,2125 MHz UL - 429,2125 MHz DL',
4292250  : '178:  419,2250 MHz UL - 429,2250 MHz DL',
4292375  : '179:  419,2375 MHz UL - 429,2375 MHz DL',
4292500  : '180:  419,2500 MHz UL - 429,2500 MHz DL',
4292625  : '181:  419,2625 MHz UL - 429,2625 MHz DL',
4292750  : '182:  419,2750 MHz UL - 429,2750 MHz DL',
4292875  : '183:  419,2875 MHz UL - 429,2875 MHz DL',
4293000  : '184:  419,3000 MHz UL - 429,3000 MHz DL',
4293125  : '185:  419,3125 MHz UL - 429,3125 MHz DL',
4293250  : '186:  419,3250 MHz UL - 429,3250 MHz DL',
4293375  : '187:  419,3375 MHz UL - 429,3375 MHz DL',
4293500  : '188:  419,3500 MHz UL - 429,3500 MHz DL',
4293625  : '189:  419,3625 MHz UL - 429,3625 MHz DL',
4293750  : '190:  419,3750 MHz UL - 429,3750 MHz DL',
4293875  : '191:  419,3875 MHz UL - 429,3875 MHz DL',
4294000  : '192:  419,4000 MHz UL - 429,4000 MHz DL',
4294125  : '193:  419,4125 MHz UL - 429,4125 MHz DL',
4294250  : '194:  419,4250 MHz UL - 429,4250 MHz DL',
4294375  : '195:  419,4375 MHz UL - 429,4375 MHz DL',
4294500  : '196:  419,4500 MHz UL - 429,4500 MHz DL',
4294625  : '197:  419,4625 MHz UL - 429,4625 MHz DL',
4294750  : '198:  419,4750 MHz UL - 429,4750 MHz DL',
4294875  : '199:  419,4875 MHz UL - 429,4875 MHz DL',
4295000  : '200:  419,5000 MHz UL - 429,5000 MHz DL',
4295125  : '201:  419,5125 MHz UL - 429,5125 MHz DL',
4295250  : '202:  419,5250 MHz UL - 429,5250 MHz DL',
4295375  : '203:  419,5375 MHz UL - 429,5375 MHz DL',
4295500  : '204:  419,5500 MHz UL - 429,5500 MHz DL',
4295625  : '205:  419,5625 MHz UL - 429,5625 MHz DL',
4295750  : '206:  419,5750 MHz UL - 429,5750 MHz DL',
4295875  : '207:  419,5875 MHz UL - 429,5875 MHz DL',
4296000  : '208:  419,6000 MHz UL - 429,6000 MHz DL',
4296125  : '209:  419,6125 MHz UL - 429,6125 MHz DL',
4296250  : '210:  419,6250 MHz UL - 429,6250 MHz DL',
4296375  : '211:  419,6375 MHz UL - 429,6375 MHz DL',
4296500  : '212:  419,6500 MHz UL - 429,6500 MHz DL',
4296625  : '213:  419,6625 MHz UL - 429,6625 MHz DL',
4296750  : '214:  419,6750 MHz UL - 429,6750 MHz DL',
4296875  : '215:  419,6875 MHz UL - 429,6875 MHz DL',
4297000  : '216:  419,7000 MHz UL - 429,7000 MHz DL',
4297125  : '217:  419,7125 MHz UL - 429,7125 MHz DL',
4297250  : '218:  419,7250 MHz UL - 429,7250 MHz DL',
4297375  : '219:  419,7375 MHz UL - 429,7375 MHz DL',
4297500  : '220:  419,7500 MHz UL - 429,7500 MHz DL',
4297625  : '221:  419,7625 MHz UL - 429,7625 MHz DL',
4297750  : '222:  419,7750 MHz UL - 429,7750 MHz DL',
4297875  : '223:  419,7875 MHz UL - 429,7875 MHz DL',
4298000  : '224:  419,8000 MHz UL - 429,8000 MHz DL',
4298125  : '225:  419,8125 MHz UL - 429,8125 MHz DL',
4298250  : '226:  419,8250 MHz UL - 429,8250 MHz DL',
4298375  : '227:  419,8375 MHz UL - 429,8375 MHz DL',
4298500  : '228:  419,8500 MHz UL - 429,8500 MHz DL',
4298625  : '229:  419,8625 MHz UL - 429,8625 MHz DL',
4298750  : '230:  419,8750 MHz UL - 429,8750 MHz DL',
4298875  : '231:  419,8875 MHz UL - 429,8875 MHz DL',
4299000  : '232:  419,9000 MHz UL - 429,9000 MHz DL',
4299125  : '233:  419,9125 MHz UL - 429,9125 MHz DL',
4299250  : '234:  419,9250 MHz UL - 429,9250 MHz DL',
4299375  : '235:  419,9375 MHz UL - 429,9375 MHz DL',
4299500  : '236:  419,9500 MHz UL - 429,9500 MHz DL',
4299625  : '237:  419,9625 MHz UL - 429,9625 MHz DL',
4299750  : '238:  419,9750 MHz UL - 429,9750 MHz DL',
4299875  : '239:  419,9875 MHz UL - 429,9875 MHz DL',
4300000  : '240:  420,0000 MHz UL - 430,0000 MHz DL'
}

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

# -----------------------------------------------------
# --  Analizar los argumentos pasados por el usuario
# --  Devuelve el puerto y otros argumentos enviados como parametros
# -----------------------------------------------------


def analizar_argumentos():

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
        sys.exit(WARNING)

    HighLevelWarningUL = int(args['highLevelWarningUplink'])
    HighLevelCriticalUL = int(args['highLevelCriticalUplink'])
    HighLevelWarningDL = int(args['highLevelWarningDownlink'])
    HighLevelCriticalDL = int(args['highLevelCriticalDownlink'])
    
    return  HighLevelWarningUL,  HighLevelCriticalUL,  HighLevelWarningDL, HighLevelCriticalDL
# ----------------------------------------------------
# -- Armar trama de escritura o lectura
#-- (PARAMETROS)
# -- Interface: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
# -- CmdNumber: 80 = Send ; 00 = Receive
# -- CmdBodyLenght: Indentica si lee o escribe
# -- CmdData: dato a escribir <integer en hex>
# -- Crc: Byte de control
# ---------------------------------------------------

# -----------------------------------------
#   convertir hex a decimal con signo
# ----------------------------------------

def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

# ----------------------
#   MAIN
# ----------------------

def main():

    # -- Analizar los argumentos pasados por el usuario
   
    hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl  = analizar_argumentos()

    frame_list = get_frame_list()


    # --------------------------------------------------------
    # -- Abrir el puerto serie. Si hay algun error se termina
    # --------------------------------------------------------
    try:
        Port = '/dev/ttyS0'
        baudrate = 19200
        s = serial.Serial(Port, baudrate)
        # -- Timeout: 1 seg
        s.timeout = 1

    except serial.SerialException:
        # -- Error al abrir el puerto serie
        sys.stderr.write(
            "CRITICAL - Error al abrir puerto %s " % str(Port))
        sys.exit(CRITICAL)

    parameter_dict = dict()

    for frame in frame_list:
        rs485.write_serial_frame(frame,s)
        hex_data_frame = rs485.read_serial_frame(Port, s)
        data = rs485.validar_trama_respuesta(hex_data_frame,'dmu',0)
        a_bytearray = bytearray(data)
        hex_validated_frame = a_bytearray.hex()
        
        try:
            resultOK =  int(hex_validated_frame, 16)
        except:
            print("WARNING - Dato recibido es desconocido")
            sys.exit(WARNING)

        cmdNumber = frame[8:10]
        set_parameter_dic_from_validated_frame(parameter_dict, hex_validated_frame, cmdNumber)
        
    s.close()
   
    dru_host_created = 0
    complete_services =  discovery.icinga_get_localhost_services()
    if (complete_services.status_code == 200):
        for opt in range(1,5):
        
            dru_connected = int(parameter_dict['opt'+str(opt)+'ConnectedRemotes'])
            dru_services_list =discovery.get_dru_services_list(complete_services,opt)

            if (dru_connected > 0 and dru_connected <8):
                for d in range(1,dru_connected+1):
                    if(d not in  dru_services_list):
                        director_resp =  discovery.director_create_dru_service(opt,d)
                        if(director_resp.status_code == 201):
                            dru_host_created += 1
    if dru_host_created > 0:
        discovery.director_deploy()
        dru_host_created = 0

    alarm = get_alarm_from_dict(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameter_dict)
    parameter_html_table = create_table(parameter_dict)      
    graphite = get_graphite_str(hl_warning_ul, hl_critical_ul, hl_warning_dl, hl_critical_dl, parameter_dict)

    sys.stderr.write(alarm+parameter_html_table+"|"+graphite)
    if( alarm != ""):
        sys.exit(WARNING)
    else:
        sys.exit(OK)

def get_frame_list():
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
    dlPower = float(parameter_dict['dlOutputPower'])
    ulPower = float(parameter_dict['ulInputPower'])


    alarm =""
    if dlPower >= hl_critical_dl:
        alarm +="<h3><font color=\"#ff5566\">Downlink Power Level Critical "
        alarm += parameter_dict['ulInputPower']
        alarm += " [dBm]!</font></h3>"
    elif dlPower >= hl_warning_dl:
        alarm +="<h3><font color=\"#ffaa44\">Downlink Power Level Warning "
        alarm += parameter_dict['ulInputPower']
        alarm += "[dBm]</font></h3>"

    if ulPower > 0:
        alarm +=""         
    elif ulPower >= hl_critical_ul:
        alarm +="<h3><font color=\"#ff5566\">Uplink Power Level Critical " 
        alarm += parameter_dict['dlOutputPower']
        alarm +="[dBm]!</font></h3>"      
    elif ulPower >= hl_warning_ul:
        alarm +="<h3><font color=\"#ffaa44\">Uplink Power Level Warning " 
        alarm += parameter_dict['dlOutputPower']
        alarm += "[dBm]</font></h3>"
        
    return alarm

def get_graphite_str(hlwul, hlcul, hlwdl, hlcdl, parameter_dict):
    ulPower = float(parameter_dict['ulInputPower'])

    if(ulPower > 0 or ulPower < -110):
        ulPower_str = "-"
    else:
        ulPower_str = parameter_dict['ulInputPower']

    ul_str  ="Uplink="+ulPower_str
    ul_str +=";"+str(hlwul)
    ul_str +=";"+str(hlcul)
    
    dl_str ="Downlink="+parameter_dict['dlOutputPower']
    dl_str +=";"+str(hlwdl)
    dl_str +=";"+str(hlcdl)
    graphite = ul_str+" "+dl_str
    return graphite

def set_parameter_dic_from_validated_frame(parameter_dict, hex_validated_frame, cmd_number):
    if cmd_number=='f8':
        parameter_dict['opt1ConnectedRemotes'] = hex_validated_frame
    elif cmd_number=='f9':
        parameter_dict['opt2ConnectedRemotes'] = hex_validated_frame
    elif cmd_number=='fa':
        parameter_dict['opt3ConnectedRemotes'] = hex_validated_frame
    elif cmd_number=='fb':
        parameter_dict['opt4ConnectedRemotes'] = hex_validated_frame
    elif cmd_number=='91':
        set_opt_status_dict(parameter_dict, hex_validated_frame)
    elif cmd_number=='9a':
        set_opt_working_status(parameter_dict, hex_validated_frame)
    elif cmd_number=='f3':
        set_power_dict(parameter_dict, hex_validated_frame)
    elif cmd_number=='42':
        set_channel_status_dict(parameter_dict, hex_validated_frame)
    elif cmd_number=='36':
        set_channel_freq_dict(parameter_dict, hex_validated_frame)
    elif cmd_number=='81':
        set_working_mode_dict(parameter_dict, hex_validated_frame)   
    elif cmd_number=='ef':
        set_power_att_dict(parameter_dict, hex_validated_frame)

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
    parameter_dict['dlOutputPower'] = str(round(dlPower,2))

    hexInvertido = hex_validated_frame[0+4:2+4]+ hex_validated_frame[2+4:4+4]
    hexInvertido2 = hex_validated_frame[2+4:4+4] + hex_validated_frame[0+4:2+4]
    hex_as_int = int(hexInvertido, 16)
    hex_as_int2 = int(hexInvertido2, 16)
    ulPower = s16(hex_as_int)/256
    ulPower2 = s16(hex_as_int2)/256

    parameter_dict['ulInputPower'] = str(round(ulPower,2))

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

def set_channel_freq_dict(parameter_dict, hex_validated_frame):
    channel = 1
    i = 0
    while channel <= 16:
        byte = hex_validated_frame[i:i+8]
        byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2]
        hex_as_int = int(byteInvertido, 16)
            #print(byte,byteInvertido,hex_as_int)
        try:
          texto = frequencyDictionary[hex_as_int]
          parameter_dict["channel"+str(channel)+"ulFreq"] = texto[4:22-6+2]
          parameter_dict["channel"+str(channel)+"dlFreq"] = texto[23:40-6+2]
          channel += 1
          i += 8
        except:
          print("WARNING - Dato recibido es desconocido ")
          print(byte,byteInvertido,hex_as_int)
          sys.exit(1)

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
        sys.exit(1)

def create_table(responseDict):

    table1 = get_opt_status_table(responseDict)
    table2 = get_power_table(responseDict)
    table3 = get_channel_table(responseDict)

    table =  "<h3><font color=\"#046c94\">"+responseDict['workingMode']+"</font></h3>"
    table += '<div class="sigma-container">'
    table += table1+table2+table3
    table += "</div>"
    return table

def get_channel_table(responseDict):
    table3 = "<table width=40%>"
    table3 += "<thead><tr style=font-size:11px>"
    table3 += "<th width='10%'><font color=\"#046c94\">Channel</font></th>"
    table3 += "<th width='10%'><font color=\"#046c94\">Status</font></th>"
    table3 += "<th width='40%'><font color=\"#046c94\">UpLink Frequency</font></th>"
    table3 += "<th width='40%'><font color=\"#046c94\">Downlink Frequency</font></th>"
    table3 += "</tr></thead><tbody>"

    if (responseDict['workingMode'] == 'Channel Mode'):
        for i in range(1,17):
            channel = str(i)
            table3 +="<tr align=\"center\" style=font-size:11px>"
            table3 +="<td>"+channel+"</td>"
            table3 +="<td>"+responseDict["channel"+str(channel)+"Status"]+"</td>"
            table3 +="<td>"+responseDict["channel"+str(channel)+"ulFreq"]+"</td>"
            table3 +="<td>"+responseDict["channel"+str(channel)+"dlFreq"]+"</td>"
            table3 +="</tr>"
    else:        
        table3 +="<tr align=\"center\" style=font-size:11px>"    
        table3 +="<td>&nbsp;</td>"
        table3 +="<td>&nbsp;</td>"
        table3 +="<td>&nbsp;</td>"
        table3 +="<td>&nbsp;</td>"
        table3 +="</tr>"

    table3 +="</tbody></table>"
    return table3

def get_power_table(responseDict):
    ulPower = float(responseDict['ulInputPower'])

    if ulPower > 0 or ulPower <-110:
        ulPower = "-"
    else:
        ulPower = responseDict['ulInputPower']

    table2 = "<table width=250>"
    table2 += "<thead>"
    table2 += "<tr  align=\"center\" style=font-size:12px>"
    table2 += "<th width='12%'><font color=\"#046c94\">Link</font></th>"
    table2 += "<th width='33%'><font color=\"#046c94\">Power</font> </th>"
    table2 += "<th width='35%'><font color=\"#046c94\">Attenuation</font></th>"
    table2 += "</tr>"
    table2 += "</thead>"
    table2 += "<tbody>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>Uplink</td><td>"+ulPower+" [dBm]</td><td>"+responseDict['ulAtt']+" [dB]</td></tr>"
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

