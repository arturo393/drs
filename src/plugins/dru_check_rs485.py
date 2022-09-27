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

import sys
import getopt
import serial
from crccheck.crc import Crc16Xmodem
import argparse
import check_rs485 as rs485

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
4300000  : '240:  420,0000 MHz UL - 430,0000 MHz DL',
4300125  : '240:  420,0125 MHz UL - 430,0125 MHz DL',
4301875  : '240:  420,1875 MHz UL - 430,1875 MHz DL'

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
    ap.add_argument("-d", "--dru", required=True, help="dru es requerido", default="")
    ap.add_argument("-o", "--opt", required=True,help="opt es requerido", default="")
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

    return args

def s8(byte):
    if byte > 127:
        return (256-byte) * (-1)
    else:
        return byte
# ----------------------
#   MAIN
# ----------------------


def main():

    # -- Analizar los argumentos pasados por el usuario
    args = analizar_argumentos()

    frame_list = list()

    # -- Armando la trama
    frame_list.append(rs485.obtener_trama('query', 'dru', '00','00','04010500040305000406050004250500044004000441040004EF0B0005160A0000','23','00', args['opt']+args['dru']))
    frame_list.append(rs485.obtener_trama('query','dru','00','00','0510040000051104000005120400000513040000051404000005150400000516040000051704000005180400000519040000051A040000051B040000051C040000051D040000051E040000051F040000','52','00',args['opt']+args['dru']))
    
    # --------------------------------------------------------
    # -- Abrir el puerto serie. Si hay algun error se termina
    # --------------------------------------------------------
    try:
        port = '/dev/ttyS1'
        baudrate = 9600
        #print('baudrate: %d' % baudrate)
        s = serial.Serial(port, baudrate)

        # -- Timeout: 1 seg
        s.timeout = 1

    except serial.SerialException:
        # -- Error al abrir el puerto serie
        sys.stderr.write(
            "CRITICAL - Error al abrir puerto %s " % str(port))
        sys.exit(2)

    # -- Mostrar el nombre del dispositivo
    #print("Puerto (%s): (%s)" % (str(Port),s.portstr))
    
    parameter_dict = dict()
    table =""
    graphite=""
    for frame in frame_list:
        rs485.write_serial_frame(frame, s)
        hexResponse = rs485.read_serial_frame(port, s)
        
        data = rs485.validar_trama_respuesta(hexResponse,'dru',5)
        a_bytearray = bytearray(data)
        resultHEX = a_bytearray.hex()
        
        try:
            resultOK =  int(resultHEX, 16)
        except:
            print("WARNING - Dato recibido es desconocido")
            sys.exit(1)
        
        data_result = get_data_result_list_from_validated_frame(data)
        set_paramter_dic_from_data_result(parameter_dict, data_result)        
        
    alarm = get_alarm_from_dict(args, parameter_dict)
    table = create_table(parameter_dict)    
    graphite = get_graphite_str(args, parameter_dict)
    
    print(alarm+table+"|"+graphite)
    if( alarm != ""):
        sys.exit(1)
    else:
        sys.exit(0)

def get_graphite_str(args, parameter_dict):
    
    hl_warning_uplink = int(args['highLevelWarningUL'])
    hl_critical_uplink = int(args['highLevelCriticalUL'])
    hl_warning_downlink = int(args['highLevelWarningDL'])
    hl_critical_downlink = int(args['highLevelCriticalDL'])
    hl_warning_temperature = int(args['highLevelWarningTemperature'])
    hl_critical_temperature = int(args['highLevelCriticalTemperature'])
    dlPower = float(parameter_dict['dlOutputPower'])
    ulPower = float(parameter_dict['ulInputPower'])
    temperature = float(parameter_dict['paTemperature'])
    
    if(dlPower == 0.0):
        dlPowerStr = "-"
    else:
        dlPowerStr = str(dlPower)
 
    pa_temperature ="Temperature="+parameter_dict['paTemperature']
    pa_temperature+=";"+str(hl_warning_temperature)
    pa_temperature+=";"+str(hl_critical_temperature)
    dlPower ="Downlink="+dlPowerStr
    dlPower+=";"+str(hl_warning_downlink)
    dlPower+=";"+str(hl_critical_downlink)
    vswr  ="VSWR="+parameter_dict['vswr']
    ulPower ="Uplink="+parameter_dict['ulInputPower']
    ulPower+=";"+str(hl_warning_uplink)
    ulPower+=";"+str(hl_critical_uplink)
    
    graphite = pa_temperature+" "+dlPower+" "+vswr+" "+ulPower
    return graphite

def get_alarm_from_dict(args, parameter_dict):
    
    hl_warning_uplink = int(args['highLevelWarningUL'])
    hl_critical_uplink = int(args['highLevelCriticalUL'])
    hl_warning_downlink = int(args['highLevelWarningDL'])
    hl_critical_downlink = int(args['highLevelCriticalDL'])
    hl_warning_temperature = int(args['highLevelWarningTemperature'])
    hl_critical_temperature = int(args['highLevelCriticalTemperature'])

    dlPower = float(parameter_dict['dlOutputPower'])
    ulPower = float(parameter_dict['ulInputPower'])
    temperature = float(parameter_dict['paTemperature'])

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


    if temperature >= hl_critical_temperature:
        alarm +="<h3><font color=\"#ff5566\">Temperature Level Critical "
        alarm += parameter_dict['paTemperature']
        alarm += " [°C]!</font></h3>"

    elif temperature >= hl_warning_temperature:
        alarm +="<h3><font color=\"#ffaa44\">Temperature Level Warning "
        alarm += parameter_dict['paTemperature']
        alarm += " [°C]!</font></h3>"

    return alarm

def create_table(parameter_dic):
    
    table1 = get_power_att_table(parameter_dic)
    table2 = get_vswr_temperature_table(parameter_dic)
    table3 = get_channel_freq_table(parameter_dic)
    
    table =  "<h3><font color=\"#046c94\">"+parameter_dic['workingMode']+"</font></h3>"
    table += '<div class="sigma-container">'
    table += table2+table1+table3
    table += "</div>"

    return table

def get_channel_freq_table(parameter_dic):
    table3 = "<table width=40%>"
    table3 += "<thead><tr style=font-size:11px>"
    table3 += "<th width='10%'><font color=\"#046c94\">Channel</font></th>"
    table3 += "<th width='10%'><font color=\"#046c94\">Status</font></th>"
    table3 += "<th width='40%'><font color=\"#046c94\">UpLink Frequency</font></th>"
    table3 += "<th width='40%'><font color=\"#046c94\">Downlink Frequency</font></th>"
    table3 += "</tr></thead><tbody>"

    if (parameter_dic['workingMode'] == 'Channel Mode'):
        for i in range(1,17):
            channel = str(i)
            table3 +="<tr align=\"center\" style=font-size:11px>"
            table3 +="<td>"+channel+"</td>"
            table3 +="<td>"+parameter_dic["channel"+str(channel)+"Status"]+"</td>"
            table3 +="<td>"+parameter_dic["channel"+str(channel)+"ulFreq"]+"</td>"
            table3 +="<td>"+parameter_dic["channel"+str(channel)+"dlFreq"]+"</td>"
            table3 +="</tr>"
    else:        
        table3 +="<tr align=\"center\" style=font-size:11px>"    
        table3 +="<td>&nbsp;</td>"
        table3 +="<td>&nbsp;</td>"
        table3 +="<td>&nbsp;</td>"
        table3 +="<td>&nbsp;</td>"
        table3 +="</tr>"
    table3+="</tbody></table>"
    return table3

def get_vswr_temperature_table(parameter_dic):
    table2  = "<table width=100>"
    table2 += "<thead>"
    table2 += "<tr  style=font-size:12px>"
    table2 += "<th width='70%'><font color=\"#046c94\">Temperature</font></th>"
    table2 += "<th width='30%'><font color=\"#046c94\">VSWR</font></th>"
    table2 += "</tr>"
    table2 += "</thead>"
    table2 += "<tbody>"
    table2 += "<tr align=\"center\" style=font-size:12px><td>"+parameter_dic['paTemperature']+" [°C]</td><td>"+parameter_dic['vswr']+"</td></tr>"
    table2 +="</tbody></table>"
    return table2

def get_power_att_table(parameter_dic):
    dlPower = parameter_dic['dlOutputPower']
    if(dlPower == str(0)):
        dlPowerStr = "-"
    else:
        dlPowerStr = str(dlPower)

    table1  = "<table width=250>"
    table1 += "<thead>"
    table1 += "<tr  align=\"center\" style=font-size:12px>"
    table1 += "<th width='12%'><font color=\"#046c94\">Link</font></th>"
    table1 += "<th width='33%'><font color=\"#046c94\">Power</font> </th>"
    table1 += "<th width='35%'><font color=\"#046c94\">Attenuation</font></th>"
    table1 += "</tr>"
    table1 += "</thead>"
    table1 += "<tbody>"
    table1 += "<tr align=\"center\" style=font-size:12px><td>Uplink</td><td>"+parameter_dic['ulInputPower']+" [dBm]</td><td>"+parameter_dic['ulAtt']+" [dB]</td></tr>"
    table1 += "<tr align=\"center\" style=font-size:12px><td>Downlink</td><td>"+dlPowerStr+" [dBm]</td><td>"+parameter_dic['dlAtt']+" [dB]</td></tr>"
    table1 +="</tbody></table>"
    return table1

def set_paramter_dic_from_data_result(parameter_dic, data_result):
    for data in data_result:
        cmd_number = data[:4]
        cmd_value = data[4:]
        
        if cmd_number =='0105':
            temperature = s8(int(cmd_value,16))
            parameter_dic['paTemperature'] = str(temperature)
                                                                                                                 
        elif cmd_number == '0305':
            dl_power = s8(int(cmd_value, 16))
            parameter_dic['dlOutputPower'] = str(dl_power)
        elif cmd_number == '2505':
            ul_power = s8(int(cmd_value, 16))
            parameter_dic['ulInputPower'] = str(ul_power)
            
        elif cmd_number == '0605':
            vswr = s8(int(cmd_value, 16))/10
            parameter_dic['vswr'] = str(round(vswr,2))
            
        elif cmd_number == '4004':
            ul_att = (int(cmd_value, 16))
            parameter_dic['ulAtt'] = str(ul_att)  
                                    
        elif cmd_number == '4104':
            dl_att = (int(cmd_value, 16))
            parameter_dic['dlAtt'] = str(dl_att)
            
        elif cmd_number == 'ef0b':
            working_mode = (int(cmd_value, 16))

            if working_mode == 2:
                parameter_dic['workingMode'] = "WideBand Mode"
            elif working_mode == 3:
                parameter_dic['workingMode'] = "Channel Mode"
            else:
                parameter_dic['workingMode'] = "Unknown"
                
        elif (cmd_number == '1004' or cmd_number == '1104' or cmd_number == '1204'
            or cmd_number == '1304' or cmd_number == '1404' or cmd_number == '1504'
            or cmd_number == '1604' or cmd_number == '1704' or cmd_number == '1804'
            or cmd_number == '1904' or cmd_number == '1a04' or cmd_number == '1b04'
            or cmd_number == '1c04' or cmd_number == '1d04' or cmd_number == '1e04'
            or cmd_number == '1f04'):
            
            byte0 = int(cmd_value[0:2], 16)   
            ch_number = int(cmd_number[1],16)+1
            channel = 4270000 + (125 * byte0)   
            text = frequencyDictionary[channel] 
            parameter_dic["channel"+str(ch_number)+"ulFreq"] = text[4:22-6+2]
            parameter_dic["channel"+str(ch_number)+"dlFreq"] = text[23:40-6+2]
        
        elif cmd_number == '160a':
            byte2 = cmd_value[0:2]
            byte1 = cmd_value[2:4]
            res1 = "{0:08b}".format(int(byte1, 16))
            res2 = "{0:08b}".format(int(byte2, 16))
            binario = res1 + res2
            channel = 0            
            for i  in binario:
                channel += 1                
                if (i == '1' ):  
                    parameter_dic["channel"+str(channel)+"Status"] = "ON"                      
                else:
                    parameter_dic["channel"+str(channel)+"Status"] = "OFF"            

def get_data_result_list_from_validated_frame(data):
    i = 0
    j = 0
    temp = list()
    dataResult = list()
    isWriting = False

    for i in range(0,len(data)-1):
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
    return dataResult

if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code     Status
# 0     OK
# 1     WARNING
# 2     CRITICAL
# 3     UNKNOWN

