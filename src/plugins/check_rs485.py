#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# ----------------------------------------------------------------------------
# check_rs485.py  Ejemplo de manejo del puerto serie desde python utilizando la
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
# -----------------------------------------------------------------------------

from pickle import FALSE, TRUE
import sys
import getopt
import serial
from crccheck.crc import Crc16Xmodem
import argparse
# --------------------------------
# -- Declaracion de constantes
# --------------------------------
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

dataDMU = {
    "F8" : "Digital Remote Units",
    "F9" : "Digital Remote Units",
    "FA" : "Digital Remote Units",
    "FB" : "Digital Remote Units",
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
    "0105" : { "unidad": " &ordm;C", "variable" : "temprature"},
    "0305" : { "unidad": " [dBm]", "variable" : "dBm" }, 
    "0605" : { "unidad": " ", "variable" : "voltage" },
    "2505" : { "unidad": " [dBm]", "variable" : "dBm" },
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
}

frequencyDictionary = {
4270000	 : '000:  417,0000 MHz UL - 427,0000 MHz DL',
4270125	 : '001:  417,0125 MHz UL - 427,0125 MHz DL',
4270250	 : '002:  417,0250 MHz UL - 427,0250 MHz DL',
4270375	 : '003:  417,0375 MHz UL - 427,0375 MHz DL',
4270500	 : '004:  417,0500 MHz UL - 427,0500 MHz DL',
4270625	 : '005:  417,0625 MHz UL - 427,0625 MHz DL',
4270750	 : '006:  417,0750 MHz UL - 427,0750 MHz DL',
4270875	 : '007:  417,0875 MHz UL - 427,0875 MHz DL',
4271000	 : '008:  417,1000 MHz UL - 427,1000 MHz DL',
4271125	 : '009:  417,1125 MHz UL - 427,1125 MHz DL',
4271250	 : '010:  417,1250 MHz UL - 427,1250 MHz DL',
4271375	 : '011:  417,1375 MHz UL - 427,1375 MHz DL',
4271500	 : '012:  417,1500 MHz UL - 427,1500 MHz DL',
4271625	 : '013:  417,1625 MHz UL - 427,1625 MHz DL',
4271750	 : '014:  417,1750 MHz UL - 427,1750 MHz DL',
4271875	 : '015:  417,1875 MHz UL - 427,1875 MHz DL',
4272000	 : '016:  417,2000 MHz UL - 427,2000 MHz DL',
4272125	 : '017:  417,2125 MHz UL - 427,2125 MHz DL',
4272250	 : '018:  417,2250 MHz UL - 427,2250 MHz DL',
4272375	 : '019:  417,2375 MHz UL - 427,2375 MHz DL',
4272500	 : '020:  417,2500 MHz UL - 427,2500 MHz DL',
4272625	 : '021:  417,2625 MHz UL - 427,2625 MHz DL',
4272750	 : '022:  417,2750 MHz UL - 427,2750 MHz DL',
4272875	 : '023:  417,2875 MHz UL - 427,2875 MHz DL',
4273000	 : '024:  417,3000 MHz UL - 427,3000 MHz DL',
4273125	 : '025:  417,3125 MHz UL - 427,3125 MHz DL',
4273250	 : '026:  417,3250 MHz UL - 427,3250 MHz DL',
4273375	 : '027:  417,3375 MHz UL - 427,3375 MHz DL',
4273500	 : '028:  417,3500 MHz UL - 427,3500 MHz DL',
4273625	 : '029:  417,3625 MHz UL - 427,3625 MHz DL',
4273750	 : '030:  417,3750 MHz UL - 427,3750 MHz DL',
4273875	 : '031:  417,3875 MHz UL - 427,3875 MHz DL',
4274000	 : '032:  417,4000 MHz UL - 427,4000 MHz DL',
4274125	 : '033:  417,4125 MHz UL - 427,4125 MHz DL',
4274250	 : '034:  417,4250 MHz UL - 427,4250 MHz DL',
4274375	 : '035:  417,4375 MHz UL - 427,4375 MHz DL',
4274500	 : '036:  417,4500 MHz UL - 427,4500 MHz DL',
4274625	 : '037:  417,4625 MHz UL - 427,4625 MHz DL',
4274750	 : '038:  417,4750 MHz UL - 427,4750 MHz DL',
4274875	 : '039:  417,4875 MHz UL - 427,4875 MHz DL',
4275000	 : '040:  417,5000 MHz UL - 427,5000 MHz DL',
4275125	 : '041:  417,5125 MHz UL - 427,5125 MHz DL',
4275250	 : '042:  417,5250 MHz UL - 427,5250 MHz DL',
4275375	 : '043:  417,5375 MHz UL - 427,5375 MHz DL',
4275500	 : '044:  417,5500 MHz UL - 427,5500 MHz DL',
4275625	 : '045:  417,5625 MHz UL - 427,5625 MHz DL',
4275750	 : '046:  417,5750 MHz UL - 427,5750 MHz DL',
4275875	 : '047:  417,5875 MHz UL - 427,5875 MHz DL',
4276000	 : '048:  417,6000 MHz UL - 427,6000 MHz DL',
4276125	 : '049:  417,6125 MHz UL - 427,6125 MHz DL',
4276250	 : '050:  417,6250 MHz UL - 427,6250 MHz DL',
4276375	 : '051:  417,6375 MHz UL - 427,6375 MHz DL',
4276500	 : '052:  417,6500 MHz UL - 427,6500 MHz DL',
4276625	 : '053:  417,6625 MHz UL - 427,6625 MHz DL',
4276750	 : '054:  417,6750 MHz UL - 427,6750 MHz DL',
4276875	 : '055:  417,6875 MHz UL - 427,6875 MHz DL',
4277000	 : '056:  417,7000 MHz UL - 427,7000 MHz DL',
4277125	 : '057:  417,7125 MHz UL - 427,7125 MHz DL',
4277250	 : '058:  417,7250 MHz UL - 427,7250 MHz DL',
4277375	 : '059:  417,7375 MHz UL - 427,7375 MHz DL',
4277500	 : '060:  417,7500 MHz UL - 427,7500 MHz DL',
4277625	 : '061:  417,7625 MHz UL - 427,7625 MHz DL',
4277750	 : '062:  417,7750 MHz UL - 427,7750 MHz DL',
4277875	 : '063:  417,7875 MHz UL - 427,7875 MHz DL',
4278000	 : '064:  417,8000 MHz UL - 427,8000 MHz DL',
4278125	 : '065:  417,8125 MHz UL - 427,8125 MHz DL',
4278250	 : '066:  417,8250 MHz UL - 427,8250 MHz DL',
4278375	 : '067:  417,8375 MHz UL - 427,8375 MHz DL',
4278500	 : '068:  417,8500 MHz UL - 427,8500 MHz DL',
4278625	 : '069:  417,8625 MHz UL - 427,8625 MHz DL',
4278750	 : '070:  417,8750 MHz UL - 427,8750 MHz DL',
4278875	 : '071:  417,8875 MHz UL - 427,8875 MHz DL',
4279000	 : '072:  417,9000 MHz UL - 427,9000 MHz DL',
4279125	 : '073:  417,9125 MHz UL - 427,9125 MHz DL',
4279250	 : '074:  417,9250 MHz UL - 427,9250 MHz DL',
4279375	 : '075:  417,9375 MHz UL - 427,9375 MHz DL',
4279500	 : '076:  417,9500 MHz UL - 427,9500 MHz DL',
4279625	 : '077:  417,9625 MHz UL - 427,9625 MHz DL',
4279750	 : '078:  417,9750 MHz UL - 427,9750 MHz DL',
4279875	 : '079:  417,9875 MHz UL - 427,9875 MHz DL',
4280000	 : '080:  418,0000 MHz UL - 428,0000 MHz DL',
4280125	 : '081:  418,0125 MHz UL - 428,0125 MHz DL',
4280250	 : '082:  418,0250 MHz UL - 428,0250 MHz DL',
4280375	 : '083:  418,0375 MHz UL - 428,0375 MHz DL',
4280500	 : '084:  418,0500 MHz UL - 428,0500 MHz DL',
4280625	 : '085:  418,0625 MHz UL - 428,0625 MHz DL',
4280750	 : '086:  418,0750 MHz UL - 428,0750 MHz DL',
4280875	 : '087:  418,0875 MHz UL - 428,0875 MHz DL',
4281000	 : '088:  418,1000 MHz UL - 428,1000 MHz DL',
4281125	 : '089:  418,1125 MHz UL - 428,1125 MHz DL',
4281250	 : '090:  418,1250 MHz UL - 428,1250 MHz DL',
4281375	 : '091:  418,1375 MHz UL - 428,1375 MHz DL',
4281500	 : '092:  418,1500 MHz UL - 428,1500 MHz DL',
4281625	 : '093:  418,1625 MHz UL - 428,1625 MHz DL',
4281750	 : '094:  418,1750 MHz UL - 428,1750 MHz DL',
4281875	 : '095:  418,1875 MHz UL - 428,1875 MHz DL',
4282000	 : '096:  418,2000 MHz UL - 428,2000 MHz DL',
4282125	 : '097:  418,2125 MHz UL - 428,2125 MHz DL',
4282250	 : '098:  418,2250 MHz UL - 428,2250 MHz DL',
4282375	 : '099:  418,2375 MHz UL - 428,2375 MHz DL',
4282500	 : '100:  418,2500 MHz UL - 428,2500 MHz DL',
4282625	 : '101:  418,2625 MHz UL - 428,2625 MHz DL',
4282750	 : '102:  418,2750 MHz UL - 428,2750 MHz DL',
4282875	 : '103:  418,2875 MHz UL - 428,2875 MHz DL',
4283000	 : '104:  418,3000 MHz UL - 428,3000 MHz DL',
4283125	 : '105:  418,3125 MHz UL - 428,3125 MHz DL',
4283250	 : '106:  418,3250 MHz UL - 428,3250 MHz DL',
4283375	 : '107:  418,3375 MHz UL - 428,3375 MHz DL',
4283500	 : '108:  418,3500 MHz UL - 428,3500 MHz DL',
4283625	 : '109:  418,3625 MHz UL - 428,3625 MHz DL',
4283750	 : '110:  418,3750 MHz UL - 428,3750 MHz DL',
4283875	 : '111:  418,3875 MHz UL - 428,3875 MHz DL',
4284000	 : '112:  418,4000 MHz UL - 428,4000 MHz DL',
4284125	 : '113:  418,4125 MHz UL - 428,4125 MHz DL',
4284250	 : '114:  418,4250 MHz UL - 428,4250 MHz DL',
4284375	 : '115:  418,4375 MHz UL - 428,4375 MHz DL',
4284500	 : '116:  418,4500 MHz UL - 428,4500 MHz DL',
4284625	 : '117:  418,4625 MHz UL - 428,4625 MHz DL',
4284750	 : '118:  418,4750 MHz UL - 428,4750 MHz DL',
4284875	 : '119:  418,4875 MHz UL - 428,4875 MHz DL',
4285000	 : '120:  418,5000 MHz UL - 428,5000 MHz DL',
4285125	 : '121:  418,5125 MHz UL - 428,5125 MHz DL',
4285250	 : '122:  418,5250 MHz UL - 428,5250 MHz DL',
4285375	 : '123:  418,5375 MHz UL - 428,5375 MHz DL',
4285500	 : '124:  418,5500 MHz UL - 428,5500 MHz DL',
4285625	 : '125:  418,5625 MHz UL - 428,5625 MHz DL',
4285750	 : '126:  418,5750 MHz UL - 428,5750 MHz DL',
4285875	 : '127:  418,5875 MHz UL - 428,5875 MHz DL',
4286000	 : '128:  418,6000 MHz UL - 428,6000 MHz DL',
4286125	 : '129:  418,6125 MHz UL - 428,6125 MHz DL',
4286250	 : '130:  418,6250 MHz UL - 428,6250 MHz DL',
4286375	 : '131:  418,6375 MHz UL - 428,6375 MHz DL',
4286500	 : '132:  418,6500 MHz UL - 428,6500 MHz DL',
4286625	 : '133:  418,6625 MHz UL - 428,6625 MHz DL',
4286750	 : '134:  418,6750 MHz UL - 428,6750 MHz DL',
4286875	 : '135:  418,6875 MHz UL - 428,6875 MHz DL',
4287000	 : '136:  418,7000 MHz UL - 428,7000 MHz DL',
4287125	 : '137:  418,7125 MHz UL - 428,7125 MHz DL',
4287250	 : '138:  418,7250 MHz UL - 428,7250 MHz DL',
4287375	 : '139:  418,7375 MHz UL - 428,7375 MHz DL',
4287500	 : '140:  418,7500 MHz UL - 428,7500 MHz DL',
4287625	 : '141:  418,7625 MHz UL - 428,7625 MHz DL',
4287750	 : '142:  418,7750 MHz UL - 428,7750 MHz DL',
4287875	 : '143:  418,7875 MHz UL - 428,7875 MHz DL',
4288000	 : '144:  418,8000 MHz UL - 428,8000 MHz DL',
4288125	 : '145:  418,8125 MHz UL - 428,8125 MHz DL',
4288250	 : '146:  418,8250 MHz UL - 428,8250 MHz DL',
4288375	 : '147:  418,8375 MHz UL - 428,8375 MHz DL',
4288500	 : '148:  418,8500 MHz UL - 428,8500 MHz DL',
4288625	 : '149:  418,8625 MHz UL - 428,8625 MHz DL',
4288750	 : '150:  418,8750 MHz UL - 428,8750 MHz DL',
4288875	 : '151:  418,8875 MHz UL - 428,8875 MHz DL',
4289000	 : '152:  418,9000 MHz UL - 428,9000 MHz DL',
4289125	 : '153:  418,9125 MHz UL - 428,9125 MHz DL',
4289250	 : '154:  418,9250 MHz UL - 428,9250 MHz DL',
4289375	 : '155:  418,9375 MHz UL - 428,9375 MHz DL',
4289500	 : '156:  418,9500 MHz UL - 428,9500 MHz DL',
4289625	 : '157:  418,9625 MHz UL - 428,9625 MHz DL',
4289750	 : '158:  418,9750 MHz UL - 428,9750 MHz DL',
4289875	 : '159:  418,9875 MHz UL - 428,9875 MHz DL',
4290000	 : '160:  419,0000 MHz UL - 429,0000 MHz DL',
4290125	 : '161:  419,0125 MHz UL - 429,0125 MHz DL',
4290250	 : '162:  419,0250 MHz UL - 429,0250 MHz DL',
4290375	 : '163:  419,0375 MHz UL - 429,0375 MHz DL',
4290500	 : '164:  419,0500 MHz UL - 429,0500 MHz DL',
4290625	 : '165:  419,0625 MHz UL - 429,0625 MHz DL',
4290750	 : '166:  419,0750 MHz UL - 429,0750 MHz DL',
4290875	 : '167:  419,0875 MHz UL - 429,0875 MHz DL',
4291000	 : '168:  419,1000 MHz UL - 429,1000 MHz DL',
4291125	 : '169:  419,1125 MHz UL - 429,1125 MHz DL',
4291250	 : '170:  419,1250 MHz UL - 429,1250 MHz DL',
4291375	 : '171:  419,1375 MHz UL - 429,1375 MHz DL',
4291500	 : '172:  419,1500 MHz UL - 429,1500 MHz DL',
4291625	 : '173:  419,1625 MHz UL - 429,1625 MHz DL',
4291750	 : '174:  419,1750 MHz UL - 429,1750 MHz DL',
4291875	 : '175:  419,1875 MHz UL - 429,1875 MHz DL',
4292000	 : '176:  419,2000 MHz UL - 429,2000 MHz DL',
4292125	 : '177:  419,2125 MHz UL - 429,2125 MHz DL',
4292250	 : '178:  419,2250 MHz UL - 429,2250 MHz DL',
4292375	 : '179:  419,2375 MHz UL - 429,2375 MHz DL',
4292500	 : '180:  419,2500 MHz UL - 429,2500 MHz DL',
4292625	 : '181:  419,2625 MHz UL - 429,2625 MHz DL',
4292750	 : '182:  419,2750 MHz UL - 429,2750 MHz DL',
4292875	 : '183:  419,2875 MHz UL - 429,2875 MHz DL',
4293000	 : '184:  419,3000 MHz UL - 429,3000 MHz DL',
4293125	 : '185:  419,3125 MHz UL - 429,3125 MHz DL',
4293250	 : '186:  419,3250 MHz UL - 429,3250 MHz DL',
4293375	 : '187:  419,3375 MHz UL - 429,3375 MHz DL',
4293500	 : '188:  419,3500 MHz UL - 429,3500 MHz DL',
4293625	 : '189:  419,3625 MHz UL - 429,3625 MHz DL',
4293750	 : '190:  419,3750 MHz UL - 429,3750 MHz DL',
4293875	 : '191:  419,3875 MHz UL - 429,3875 MHz DL',
4294000	 : '192:  419,4000 MHz UL - 429,4000 MHz DL',
4294125	 : '193:  419,4125 MHz UL - 429,4125 MHz DL',
4294250	 : '194:  419,4250 MHz UL - 429,4250 MHz DL',
4294375	 : '195:  419,4375 MHz UL - 429,4375 MHz DL',
4294500	 : '196:  419,4500 MHz UL - 429,4500 MHz DL',
4294625	 : '197:  419,4625 MHz UL - 429,4625 MHz DL',
4294750	 : '198:  419,4750 MHz UL - 429,4750 MHz DL',
4294875	 : '199:  419,4875 MHz UL - 429,4875 MHz DL',
4295000	 : '200:  419,5000 MHz UL - 429,5000 MHz DL',
4295125	 : '201:  419,5125 MHz UL - 429,5125 MHz DL',
4295250	 : '202:  419,5250 MHz UL - 429,5250 MHz DL',
4295375	 : '203:  419,5375 MHz UL - 429,5375 MHz DL',
4295500	 : '204:  419,5500 MHz UL - 429,5500 MHz DL',
4295625	 : '205:  419,5625 MHz UL - 429,5625 MHz DL',
4295750	 : '206:  419,5750 MHz UL - 429,5750 MHz DL',
4295875	 : '207:  419,5875 MHz UL - 429,5875 MHz DL',
4296000	 : '208:  419,6000 MHz UL - 429,6000 MHz DL',
4296125	 : '209:  419,6125 MHz UL - 429,6125 MHz DL',
4296250	 : '210:  419,6250 MHz UL - 429,6250 MHz DL',
4296375	 : '211:  419,6375 MHz UL - 429,6375 MHz DL',
4296500	 : '212:  419,6500 MHz UL - 429,6500 MHz DL',
4296625	 : '213:  419,6625 MHz UL - 429,6625 MHz DL',
4296750	 : '214:  419,6750 MHz UL - 429,6750 MHz DL',
4296875	 : '215:  419,6875 MHz UL - 429,6875 MHz DL',
4297000	 : '216:  419,7000 MHz UL - 429,7000 MHz DL',
4297125	 : '217:  419,7125 MHz UL - 429,7125 MHz DL',
4297250	 : '218:  419,7250 MHz UL - 429,7250 MHz DL',
4297375	 : '219:  419,7375 MHz UL - 429,7375 MHz DL',
4297500	 : '220:  419,7500 MHz UL - 429,7500 MHz DL',
4297625	 : '221:  419,7625 MHz UL - 429,7625 MHz DL',
4297750	 : '222:  419,7750 MHz UL - 429,7750 MHz DL',
4297875	 : '223:  419,7875 MHz UL - 429,7875 MHz DL',
4298000	 : '224:  419,8000 MHz UL - 429,8000 MHz DL',
4298125	 : '225:  419,8125 MHz UL - 429,8125 MHz DL',
4298250	 : '226:  419,8250 MHz UL - 429,8250 MHz DL',
4298375	 : '227:  419,8375 MHz UL - 429,8375 MHz DL',
4298500	 : '228:  419,8500 MHz UL - 429,8500 MHz DL',
4298625	 : '229:  419,8625 MHz UL - 429,8625 MHz DL',
4298750	 : '230:  419,8750 MHz UL - 429,8750 MHz DL',
4298875	 : '231:  419,8875 MHz UL - 429,8875 MHz DL',
4299000	 : '232:  419,9000 MHz UL - 429,9000 MHz DL',
4299125	 : '233:  419,9125 MHz UL - 429,9125 MHz DL',
4299250	 : '234:  419,9250 MHz UL - 429,9250 MHz DL',
4299375	 : '235:  419,9375 MHz UL - 429,9375 MHz DL',
4299500	 : '236:  419,9500 MHz UL - 429,9500 MHz DL',
4299625	 : '237:  419,9625 MHz UL - 429,9625 MHz DL',
4299750	 : '238:  419,9750 MHz UL - 429,9750 MHz DL',
4299875	 : '239:  419,9875 MHz UL - 429,9875 MHz DL',
4300000	 : '240:  420,0000 MHz UL - 430,0000 MHz DL'			
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

# -----------------------------------------------------
# --  Analizar los argumentos pasados por el usuario
# --  Devuelve el puerto y otros argumentos enviados como parametros
# -----------------------------------------------------


def analizar_argumentos():

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
                    help="highLevelWarning es requerido", default=0)
    ap.add_argument("-lc", "--lowLevelCritical", required=False,
                    help="lowLevelCritical es requerido", default=0)
    ap.add_argument("-hc", "--highLevelCritical", required=False,
                    help="highLevelCritical es requerido", default=0)
                                                    

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
        sys.stderr.write("RS485 CRITICAL - El puerto es obligatorio\n")
        sys.exit(2)

    if Device == "":
        sys.stderr.write("RS485 CRITICAL - El device es obligatorio\n")
        sys.exit(2)

    if DmuDevice1 == "" and Device == 'dmu':
        sys.stderr.write(
            "RS485 CRITICAL - El dmuDevice1 es obligatorio\n")
        sys.exit(2)

    if DmuDevice2 == "" and Device == 'dmu':
        sys.stderr.write(
            "RS485 CRITICAL - El dmuDevice2 es obligatorio\n")
        sys.exit(2)

    if CmdNumber == "":
        sys.stderr.write("RS485 CRITICAL - cmdNumber es obligatorio\n")
        sys.exit(2)

    if (CmdBodyLenght == "" and Action == 'set') or (CmdBodyLenght == "" and Device == 'dru'):
        sys.stderr.write(
            "RS485 CRITICAL - cmdBodyLenght es obligatorio")
        sys.exit(2)

    if (CmdData == "" and Action == 'set') or (CmdData == "" and Device == 'dru'):
        sys.stderr.write("RS485 CRITICAL - cmdData es obligatorio")
        sys.exit(2)

    if (DruId == "" and Device == 'dru'):
        sys.stderr.write("RS485 CRITICAL - DruId es obligatorio")
        sys.exit(2)

    return Port, Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId, LowLevelWarning, HighLevelWarning, LowLevelCritical, HighLevelCritical


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
    return checksum_new

# ----------------------------------------------------
# -- Buscan un elemento dentro de una array
# --------------------------------------------------
def buscaArray(lst, value):

    try:
       ndx = lst.index(value)
    except:
      ndx = -1

    return ndx
# ----------------------------------------------------
# -- Formateria formato cadena de byte a Hex
# --------------------------------------------------


def formatearHex(dato):

    if dato[0:2] == '0x':
        dato_hex = dato[2:]
    else:
        dato_hex = dato

    return dato_hex
# ----------------------------------------------------
# -- Armar trama de escritura o lectura
#-- (PARAMETROS)
# -- Interface: ID de PA ó DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
# -- CmdNumber: 80 = Send ; 00 = Receive
# -- CmdBodyLenght: Indentica si lee o escribe
# -- CmdData: dato a escribir <integer en hex>
# -- Crc: Byte de control
# ---------------------------------------------------


def obtener_trama(Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId):

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
            sys.stderr.write(
                "RS485 CRITICAL - CmdBodyLenght no tiene formato hexadecimal")
            sys.exit(2)
        tramaLengthCodeData = CmdBodyLenght_hex + CmdNumber_hex + CmdData_hex
        #print('tramaLengthCodeData: %s' % tramaLengthCodeData)
        lenTramaLengthCodeData = int(len(tramaLengthCodeData)/2)
        #print('lenTramaLengthCodeData: %s' % lenTramaLengthCodeData)
        if lenTramaLengthCodeData != cant_bytes:
            sys.stderr.write(
                "RS485 CRITICAL - CmdBodyLenght + CmdNumber + CmdData, no corresponde a la cantidad de bytes indicados\n")
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
        cmd_string = C_UNKNOWN2BYTE01 + C_SITE_NUMBER + DruId_hex + C_UNKNOWN2BYTE02 + C_TXRXS_80 + \
            C_UNKNOWN1BYTE + MessageType + C_TXRXS_FF + \
            CmdBodyLenght_hex + CmdNumber_hex + CmdData_hex
    else:
        cmd_string = DmuDevice1_hex + DmuDevice2_hex + C_DATA_TYPE + \
            CmdNumber_hex + C_RESPONSE_FLAG + CmdBodyLenght_hex + CmdData_hex

    #print('La trama corta: %s' % cmd_string)
    checksum = getChecksum(cmd_string)  # calcula CRC

    trama = C_HEADER + cmd_string + checksum + C_END + Retunr_hex

    #print('Query: %s' % trama)
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
            sys.stderr.write(
                "RS485 CRITICAL - Error trama de salida invalida\n")
            sys.exit(2)
        if Device == 'dru':
            #print('Entro aqui')
            byte_respuesta = 14  # Para equipos remotos  de la trama
            cant_bytes_resp = int(hexResponse[byte_respuesta])
            rango_i = byte_respuesta + 3
            rango_n = rango_i + cant_bytes_resp - 3
        else:
            byte_respuesta = 6
            cant_bytes_resp = int(hexResponse[byte_respuesta])
            rango_i = byte_respuesta + 1
            rango_n = rango_i + cant_bytes_resp

        #print('Cant Byte respuesta: %d' % cant_bytes_resp)
        #print('longitud trama: %d' % len(hexResponse))
        #print('Rango i: %d' % rango_i)
        #print('Rango n: %d' % rango_n)
        for i in range(rango_i, rango_n):
            data.append(hexResponse[i])
        #print("Resultado de la Query es:")
        # print(data)
        return data
    except ValueError:
        sys.stderr.write(
            "RS485 CRITICAL - Error al leer trama de salida\n")
        sys.exit(2)
# -----------------------------------------
#   convertir hex a decimal con signo
# ----------------------------------------
def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

# ----------------------------------------------------------------
#   convierte la salida en hex a un valor representacion humana
# ---------------------------------------------------------------
def convertirRespuesta(Result, Device, CmdNumber):
    try:
        CmdNumber = CmdNumber.upper()
        Device = Device.lower()
        if Device=='dmu' and (CmdNumber=='F8' or CmdNumber=='F9' or CmdNumber=='FA' or CmdNumber=='FB'):
            Value =  int(Result, 16)
            Result = str(Value) + " " + dataDMU[CmdNumber] + "|value=" + str(Value) 
        
        elif  Device=='dmu' and CmdNumber=='91':
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>OPT</th><th width='15%'>VALUE</th><th width='70%'>&nbsp;</th></tr></thead><tbody>"
            if (Result[0:2] == '00'):
                Table += "<tr><td>1</td><td>ON</td><td>&nbsp;</td></tr>"
                #opt1 = '<br>OPT1: <b>ON</b> '
            else:
                Table += "<tr><td>1</td><td>OFF</td><td>&nbsp;</td></tr>" 
                #opt1 = '<br>OPT1: <b>OFF</b> '  

            if (Result[2:4] == '00'):
                Table += "<tr><td>2</td><td>ON</td><td>&nbsp;</td></tr>"
                #opt2 = '<br>OPT2: <b>ON</b> '
            else:
                Table += "<tr><td>2</td><td>OFF</td><td>&nbsp;</td></tr>" 
                #opt2 = '<br>OPT2: <b>OFF</b> '

            if (Result[4:6] == '00'):
                Table += "<tr><td>3</td><td>ON</td><td>&nbsp;</td></tr>"
                #opt3 = '<br>OPT3: <b>ON</b> '
            else: 
                Table += "<tr><td>3</td><td>OFF</td><td>&nbsp;</td></tr>"
                #opt3 = '<br>OPT3: <b>OFF</b> '
            
            if (Result[6:8] == '00'):
                Table += "<tr><td>4</td><td>ON</td><td>&nbsp;</td></tr>"
                #opt4 = '<br>OPT4: <b>ON</b> '
            else: 
                #opt4 = '<br>OPT4: <b>OFF</b> ' 
                Table += "<tr><td>4</td><td>OFF</td><td>&nbsp;</td></tr>"   
            Table +=   "</tbody></table>"             
            #Result =  opt1 + opt2 + opt3 + opt4
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
                    temp.append('Transsmision normal')
                elif (bit=='1' and opt>4):
                    temp.append('Transsmision failure')
                opt=opt+1          
            #opt1 = "<br>OPT1: " + temp[0] + temp[4] 
            #opt2 = "<br>OPT2: " + temp[1] + temp[5]
            #opt3 = "<br>OPT3: " + temp[2] + temp[6]
            #opt4 = "<br>OPT4: " + temp[3] + temp[7] 
            #Result = opt1 + opt2 + opt3 + opt4
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>OPT</th><th width='20%'>STATUS</th><th width='20%'>TRANSMISSION</th><th>&nbsp;</th></tr></thead><tbody>"
            Table += "<tr><td>1</td><td>" + temp[0]  + "</td><td>" + temp[4] + "</td><td>&nbsp;</td></tr>"
            Table += "<tr><td>2</td><td>" + temp[1]  + "</td><td>" + temp[5] + "</td><td>&nbsp;</td></tr>"
            Table += "<tr><td>3</td><td>" + temp[2]  + "</td><td>" + temp[6] + "</td><td>&nbsp;</td></tr>"
            Table += "<tr><td>4</td><td>" + temp[3]  + "</td><td>" + temp[7] + "</td><td>&nbsp;</td></tr>"
            Table += "</tbody></table>" 
            Result = Table

        elif (Device=='dmu' and CmdNumber=='F3'):    
            hexInvertido = Result[2:4] + Result[0:2]
            hex_as_int = int(hexInvertido, 16)
            decSigned = s16(hex_as_int)
            rbm = decSigned/256
            formato = '{:,.2f}'.format(rbm).replace(",", "@").replace(".", ",").replace("@", ".")
            Result = formato + " [dBm] |power=" + str(rbm)

        elif (Device=='dmu' and CmdNumber=='42'):    
            i = 0
            tmp = ''
            channel = 1
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>CHANNEL</th><th width='15%'>VALUE</th><th width='70%'>&nbsp;</th></tr></thead><tbody>"
            while channel <= 16 and i < len(Result):
                hex_as_int = int(Result[i:i+2], 16)
                if hex_as_int == 0:
                    #tmp += "<br> CH " + str(channel).zfill(2) + " ON "
                    Table += "<tr><td>"+ str(channel).zfill(2) + "</td><td>ON</td><td>&nbsp;</td></tr>"
                else:
                    #tmp += "<br> CH " + str(channel).zfill(2) + " OFF "
                    Table += "<tr><td>"+ str(channel).zfill(2) + "</td><td>OFF</td><td>&nbsp;</td></tr>"
                i += 2
                channel += 1
            Table +=   "</tbody></table>"
            #Result = tmp
            Result = Table

        elif (Device=='dmu' and CmdNumber=='36'): 
            channel = 1
            i = 0
            tmp = ''
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='25%'>CHANNEL - SUBCHANNEL</th><th width='25%'>UPLINK FRECUENCY MHZ</th><th width='50%'>DOWNLINK FRECUENCY MHZ</th></tr></thead><tbody>"
            while channel <= 16:
                byte = Result[i:i+8]
                byteInvertido = byte[6:8] + byte[4:6] + byte[2:4] + byte[0:2]             
                hex_as_int = int(byteInvertido, 16)
                #tmp += "<br> CH " + str(channel).zfill(2) + "-" + frequencyDictionary[hex_as_int]
                texto = frequencyDictionary[hex_as_int]
                Table += "<tr><td>" + str(channel).zfill(2) + "-" +  texto[0:3] + "</td><td>" + texto[4:22]  + "</td><td>" + texto[23:40] + "</td></tr>"
                channel += 1
                i += 8
            Table +=   "</tbody></table>"    
            #Result = tmp
            Result = Table
        
        elif (Device=='dmu' and CmdNumber=='81'):
            tmp = ''
            if Result == '01':
                tmp = 'Channel Mode ' 
            elif Result == '02':
                tmp = 'W ideBand Mode '
            else:
                tmp = 'Unknown '
            Result = tmp     
        
        elif (Device=='dmu' and CmdNumber=='EF'):
            byte01toInt = int(Result[0:2], 16)/4
            byte02toInt = int(Result[2:4], 16)/4
            valor1 = '{:,.2f}'.format(byte01toInt).replace(",", "@").replace(".", ",").replace("@", ".")
            valor2 = '{:,.2f}'.format(byte02toInt).replace(",", "@").replace(".", ",").replace("@", ".")
            Result = valor1 + " Uplink ATT [dB] - " + valor2 + " Downlink ATT [dB] "
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
             decSigned = s16(int(Result, 16))
             formato = '{:,.2f}'.format(decSigned).replace(",", "@").replace(".", ",").replace("@", ".")
             tmp =  str(formato) +  list['unidad'] + "|" + list['variable'] + "=" + str(decSigned)
             Result = tmp 

        elif (Device=='dru' and (CmdNumber=='0605' )):
             list = dataDRU[CmdNumber]
             decSigned = s16(int(Result, 16))/10
             formato = '{:,.2f}'.format(decSigned).replace(",", "@").replace(".", ",").replace("@", ".")
             tmp =  str(formato) +  list['unidad'] + "|" + list['variable'] + "=" + str(decSigned)
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
            #tmp = ''
            Table = "<table class='common-table table-row-selectable' data-base-target='_next'>"
            Table += "<thead><tr><th width='15%'>OPT</th><th width='15%'>VALUE</th><th width='70%'>&nbsp;</th></tr></thead><tbody>"
            for i  in binario:
                channel += 1
                if (i == '1' ):
                    #tmp +=  '<br>CH ' +  str(channel).zfill(2) + ' ON ' 
                    Table += "<tr><td>" + str(channel).zfill(2) + "</td><td>ON</td><td>&nbsp;</td></tr>"                             
                else:
                    Table += "<tr><td>" + str(channel).zfill(2) + "</td><td>OFF</td><td>&nbsp;</td></tr>"
                    #tmp +=  '<br>CH ' +  str(channel).zfill(2) + ' OFF '
            #Result = tmp
            Table +=   "</tbody></table>"
            Result = Table
        
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
        
        return Result
    except :
        sys.stderr.write("RS485 CRITICAL - Error al convertir dato de salida: " + Result)
        sys.exit(2)    
# ----------------------
#   MAIN
# ----------------------


def main():

    # -- Analizar los argumentos pasados por el usuario
    Port, Action, Device, DmuDevice1, DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId, LowLevelWarning, HighLevelWarning, LowLevelCritical, HighLevelCritical  = analizar_argumentos()

    # -- Armando la trama
    Trama = obtener_trama(Action, Device, DmuDevice1,
                          DmuDevice2, CmdNumber, CmdBodyLenght, CmdData, DruId)

    # --------------------------------------------------------
    # -- Abrir el puerto serie. Si hay algun error se termina
    # --------------------------------------------------------
    try:
        if Port == '/dev/ttyS0':
            baudrate = 19200
        else:
            baudrate = 9600
        #print('baudrate: %d' % baudrate)
        s = serial.Serial(Port, baudrate)

        # -- Timeout: 1 seg
        s.timeout = 1

    except serial.SerialException:
        # -- Error al abrir el puerto serie
        sys.stderr.write(
            "RS485 CRITICAL - Error al abrir puerto %s " % str(Port))
        sys.exit(2)

    # -- Mostrar el nombre del dispositivo
    #print("Puerto (%s): (%s)" % (str(Port),s.portstr))

    if Action == "query" or Action == "set":
        cmd_bytes = bytearray.fromhex(Trama)
        # print(cmd_bytes)
        hex_byte = ''
        for cmd_byte in cmd_bytes:
            hex_byte = ("{0:02x}".format(cmd_byte))
            s.write(bytes.fromhex(hex_byte))
        s.flush()
        #hexResponse = s.readline()

        hexadecimal_string = ''
        rcvHexArray = list()
        isDataReady = False
        rcvcount = 0
        while not isDataReady and rcvcount < 200:
            Response = s.read()
            rcvHex = Response.hex()
            #print('rcvHex: [' + rcvHex + ']')
            if(rcvHex == ''):
                isDataReady = True
                s.write(b'\x7e')
                sys.stderr.write(
                    "RS485 CRITICAL - No hay respuesta en el puerto de salida %s \n" % str(Port))
                sys.exit(2)
            elif(rcvcount == 0 and rcvHex == '7e'):
                rcvHexArray.append(rcvHex)
                hexadecimal_string = hexadecimal_string + rcvHex
                rcvcount = rcvcount + 1
            elif(rcvcount > 0 and rcvHexArray[0] == '7e' and (rcvcount == 1 and rcvHex == '7e') is not True):
                rcvHexArray.append(rcvHex)
                hexadecimal_string = hexadecimal_string + rcvHex
                rcvcount = rcvcount + 1
                if(rcvHex == '7e' or rcvHex == '7f'):
                    isDataReady = True

        hexResponse = bytearray.fromhex(hexadecimal_string)
        #print("Answer byte: ")
        # print(hexResponse)
        #print("Answer Hex: ")
        # print(rcvHexArray)

        # Aqui se realiza la validacion de la respuesta
        data = validar_trama_respuesta(hexResponse, Device)

        if Action == 'set':
            if len(data) != 0 and Device == 'dmu':
                sys.stderr.write(
                    "RS485 CRITICAL - error al escribir puerto dmu %s \n" % str(Port))
                sys.exit(2)
            elif len(data) == 0 and Device == 'dru':
                sys.stderr.write(
                    "RS485 CRITICAL - error al escribir puerto dru %s \n" % str(Port))
                sys.exit(2)
            else:
                if Device == 'dru':
                    a_bytearray = bytearray(data)
                    hex_string = a_bytearray.hex()
                    sys.stderr.write(hex_string + '\n')
                sys.stderr.write("RS485 OK")
        else:
            a_bytearray = bytearray(data)
            resultHEX = a_bytearray.hex()
            resultOK =  int(resultHEX, 16)
           
            hex_string =  convertirRespuesta(resultHEX, Device, CmdNumber)

            if ( resultOK  in range (LowLevelCritical, HighLevelCritical) ):
                print("RS485 CRITICAL - " + hex_string )
                sys.exit(2)
            elif (resultOK in range (LowLevelWarning, HighLevelWarning) ):
                print("RS485 WARNING - " + hex_string  )
                sys.exit(1)
            else:
                print("RS485 OK - " + hex_string )
                sys.exit(0)
        s.close()
    else:
        sys.stderr.write(
            "RS485 WARNING - Accion invalida:  %s \n" % Action)
        sys.exit(1)


if __name__ == "__main__":
    main()

# Nagios Exit Codes
# Exit Code	Status
# 0	OK
# 1	WARNING
# 2	CRITICAL
# 3	UNKNOWN
