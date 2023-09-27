#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

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

from dis import disco
from fcntl import F_SEAL_SEAL
from pickle import FALSE, TRUE
import sys
import getopt
import serial
import time
from crccheck.crc import Crc16Xmodem
import argparse
# importing the requests library
import requests
import json
import socket
import urllib3
import re
import check_rs485 as rs485
import time
import re
import logging

path = "/home/sigmadev/"
logging.basicConfig(format='%(asctime)s %(message)s',filename=path+"dru_check_rs485.log", level=logging.DEBUG)


urllib3.disable_warnings()
# --------------------------------
# -- Declaracion de constantes
# --------------------------------


class DRU:
    def __init__(self, dru, opt, mac,sn, name):
        self.dru = dru
        self.opt = opt
        self.mac = mac
        self.name = name
        self.sn = sn
    def __repr__(self):
         return "DRU()"
    def __str__(self):
         return "RU"+str(self.opt)+str(self.dru)+" mac:"+str(self.mac)+" sn:"+str(self.sn)
    def __eq__(self, other):
        return self.dru == other.position and self.opt == other.position and self.mac == other.mac and self.sn == other.sn

DRU_NAME_LENGHT = 4

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

ZONES_CONF = '/etc/icinga2/zones.conf'

director_api_login = "admin"
director_api_password = "Admin.123"

icinga_api_login = "root"
icinga_api_password = "Admin.123"
# --------------------------------
# -- Imprimir mensaje de ayuda
# --------------------------------
# ----------------------
#   MAIN
# ----------------------


def main():

    queries = getDmuQueries()
    start_time = time.time()
    parameters = getParametersFromQueries(queries)
    parameters["rt"] = str(time.time() - start_time)
    start_time = time.time()
    discovery_str = druDiscovery(parameters)
    parameters["dt"] = str(time.time() - start_time)
    graphite = getGraphiteMessage(parameters)
    sys.stderr.write("Summary - "+discovery_str)
    sys.stderr.write("|"+graphite)
    sys.exit(OK)

def getParametersFromQueries(queries):
    serial = rs485.setSerial('/dev/ttyS0',19200)
    replies = rs485.writeSerialQueries(queries,serial)
    parameters = rs485.getParametersFromDmuReplies(queries, replies)
    return parameters

def getGraphiteMessage(parameters):
    rt = parameters['rt']
    dt = parameters['dt']

    rt_str = "RT="+rt
    rt_str += ";"+str(1)
    rt_str += ";"+str(1)

    dt_str = "DT="+dt
    dt_str += ";"+str(2)
    dt_str += ";"+str(2)
    graphite = rt_str+" "+dt_str
    return graphite

def getDmuQueries():
    frame_list = list()
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'f8', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'f9', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'fa', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'fb', '01', '00', '00'))
        
    return frame_list

def set_parameter_dic_from_validated_frame(parameter_dict, hex_validated_frame, cmd_number):
    if cmd_number == 'f8':
        parameter_dict['opt1ConnectedRemotes'] = hex_validated_frame
    elif cmd_number == 'f9':
        parameter_dict['opt2ConnectedRemotes'] = hex_validated_frame
    elif cmd_number == 'fa':
        parameter_dict['opt3ConnectedRemotes'] = hex_validated_frame
    elif cmd_number == 'fb':
        parameter_dict['opt4ConnectedRemotes'] = hex_validated_frame

def dru_compare_mac_and_sn(found,created):
    if((found.mac == created.mac.swapcase() or found.mac == created.mac ) and (found.sn == created.sn.swapcase() or found.sn == created.sn.swapcase()) ):
        return True
    else:
        return False

def druDiscovery(parameters):
    created_dru = getCreatedDruServices()
    connected_dru = getConnectedDruServices(parameters)
    new_dru = getNewListFromConnectedEqualCreated(connected_dru, created_dru)
    removeFromNewEqualOptConnectedAndCreated(connected_dru, new_dru, created_dru)
    createNewDruService(new_dru)
    return createSumaryMessage(connected_dru, new_dru, created_dru)

def getConnectedDruServices(parameters):
    queries = getConnectedDruQueries(parameters)
    serial = rs485.setSerial('/dev/ttyS1', 9600)
    replies = rs485.writeSerialQueries(queries,serial)
    discovery = list(zip(queries,replies))
    connected_dru = getConnectedDruFromQueries(discovery)
    return connected_dru

def getCreatedDruServices():
    icinga_services = getIcingaLocalhostServices()
    if (icinga_services.status_code != 200):
        return []
    created_dru = exctractDruServices(icinga_services)
    return created_dru

def getNewListFromConnectedEqualCreated(connected_dru, created_dru):
    new_dru = list()
    for connected in connected_dru:
        not_in_created = True
        for created in created_dru:
            if(dru_compare_mac_and_sn(connected,created)):
                if (connected.port != created.port):
                    ru_created_name = "RU" + \
                                      str(created.port) + str(created.position)
                    ru_found_name = "RU" + str(connected.port) + str(connected.position)
                    if(created.name.find(ru_created_name) == -1):
                        name = created.name +"-"+ru_found_name
                    else:
                        name = created.name.replace(ru_created_name, ru_found_name)
                    not_in_new = True
                    for new in new_dru:
                        if (new.mac == connected.mac and new.sn == connected.sn) :
                            not_in_new = False

                            if (len(name) > DRU_NAME_LENGHT):
                                new.name = name
                    if (not_in_new):
                        new_dru.append(
                            DRU(connected.position, connected.port, connected.mac, connected.sn, name))

                    not_in_created = False
                else:
                    if (connected.position == created.position):
                        not_in_created = False

        if (not_in_created):
            name = "RU" + str(connected.port) + str(connected.position)
            new_dru.append(DRU(connected.position, connected.port, connected.mac, connected.sn, name))
    return new_dru

def createSumaryMessage(connected_dru, new_dru, created_dru):
    detected_str = "Connected: " + str(len(connected_dru))
    new_str = " New: " + str(len(new_dru))
    created_str = " Created: " + str(len(created_dru))

    return detected_str+" "+created_str+" "+new_str

def createNewDruService(new_dru):
    dru_host_created = 0

    for new in new_dru:
        if(new.sn != ''):
            director_resp = director_create_dru_service(new)
            if (director_resp.status_code == 201):
                dru_host_created += 1
    if dru_host_created > 0:
        director_deploy()

def removeFromNewEqualOptConnectedAndCreated(connected_dru, new_dru, created_dru):
    for connected in connected_dru:
        for created in created_dru:
            if (dru_compare_mac_and_sn(connected,created)):
                if (connected.port == created.port):
                    if (connected.position == created.position):
                        for new in new_dru:
                            if (new.mac == connected.mac and new.sn == connected.sn):
                                new_dru.remove(new)

def getConnectedDruFromQueries(discovery):
    parameters = rs485.newBlankDruParameter()
    connected_dru = list()
    reply_errors_count = 0
    for discover in discovery:
        query = discover[0]
        reply = discover[1]     
        QUERY_ID_INDEX = 14
        query_id = query[QUERY_ID_INDEX:QUERY_ID_INDEX+2]
        logging.debug("[Discovery] RU"+query_id+ " Query: "+str(query).lower())
        reply_temp = ''.join(format(x, '02x') for x in reply)
        logging.debug("[Discovery] RU"+query_id+ " Reply: "+str(reply_temp))
        if rs485.hasDruReplyError(reply,query_id):
            reply_errors_count +=1
        else:
            rs485.updateParametersWithReplyData(parameters, reply)
            REPLY_ID_INDEX = 7
            reply_id = hex(reply[REPLY_ID_INDEX])
            reply_id =reply_id[2:]
            opt = int(reply_id[0])
            dru = int(reply_id[1])
            name_found="RU"+str(opt)+str(dru)
            mac = parameters['mac']
            sn = parameters['sn']
            if isValidMACAddress(mac):
                time.sleep(0.7)
                if isValidSN(sn):
                    connected_dru.append(
                            DRU(dru,opt, mac,sn,name_found ))
                            
    return connected_dru

def director_deploy():
    master_host = get_master_host()
    director_url = "http://"+master_host+"/director/config/deploy"
    director_headers = {
        'Accept': 'application/json',
        'X-HTTP-Method-Override': 'POST'
    }

    try:
        q = requests.post(director_url,
                          headers=director_headers,
                          auth=(director_api_login, director_api_password),
                          verify=False)
    except:
        print("no connection")
        sys.exit(0)

    return q

def director_create_dru_host(opt, dru):

    hostname = socket.gethostname()
    ip_addr = socket.gethostbyname(hostname)
    master_host = get_master_host()

    if (dru == "dru1"):
        parent = hostname
    else:
        druid = int(dru[3:]) - 1
        parent = hostname+"-"+opt+"-dru"+str(druid)

    director_query = {
        'object_name': hostname+"-"+opt+"-"+dru,
        "object_type": "object",
        "zone": hostname,
        "address": ip_addr,
        "imports": ["dmu-opt-dru-host-template"],
        "display_name": "Remote " + dru[3:]+"("+opt+")",
        "vars": {
            "opt": opt[3:],
            "dru": dru[3:],
            "parents": [parent]
        }
    }

    request_url = "http://"+master_host+"/director/host"
    headers = {
        'Accept': 'application/json',
        'X-HTTP-Method-Override': 'POST'
    }

    try:
        q = requests.post(request_url,
                          headers=headers,
                          data=json.dumps(director_query),
                          auth=(director_api_login, director_api_password),
                          verify=False)

    except:
        print("no connection")
        sys.exit(0)

    # print(json.dumps(q.json(),indent=2))
    return q

def director_create_dru_service(service):

    hostname = socket.gethostname()
    master_host = get_master_host()
    opt = service.port
    dru = service.position
    mac = service.mac
    name = service.name
    display_name = "RU"+str(opt)+str(dru)
    sn = service.sn
    if (dru == 1):
        parent = hostname
    else:
        parent = hostname+"-opt"+str(opt)+"-dru"+str(dru-1)

    director_query = {
        'object_name': name,
#        'display_name':display_name,
        "object_type": "object",
        "host": hostname,
        "imports": ["dmu-dru-command-service-template"],
        "vars": {
            "opt": opt,
            "dru": dru,
            "mac": mac,
            "sn": sn,
            "parents": [parent]
        }
    }

    request_url = "http://"+master_host+"/director/service"
    headers = {
        'Accept': 'application/json',
        'X-HTTP-Method-Override': 'POST'
    }

    try:
        q = requests.post(request_url,
                          headers=headers,
                          data=json.dumps(director_query),
                          auth=(director_api_login, director_api_password),
                          verify=False)

    except:
        print("no connection")
        sys.exit(0)

    # print(json.dumps(q.json(),indent=2))
    return q

def director_create_dru_applyservices(opt, dru):

    service_name = "dlPower-2"
    master_hostname = socket.gethostname()
    master_host = get_master_host()
    remote_hostname = master_hostname+"-opt"+opt[3:]+"-dru"+dru[3:]
    imports = list()

    # the names are from service templates
    imports.append(("Downlink Power", "dlPower"))
    imports.append(("Uplink Power", "ulPower"))
    imports.append(("Power Amplifier Temperature", "paTemperature"))
    imports.append(("VSWR", "vswr"))

    for template in imports:

        director_query = {
            "assign_filter": "host.name=%22"+remote_hostname+"\"",
            # "check_command": master_hostname+"-service-command",
            "imports": ["dmu-dru-query-"+template[1]+"-template"],
            "object_name": template[0],
            "object_type": "apply",
            "vars": {
                "druID": opt[3:]+dru[3:]
            }
        }

        headers = {
            'Accept': 'application/json',
            'X-HTTP-Method-Override': 'POST'
        }

        request_url = "http://"+master_host+"/director/service"

        try:
            q = requests.post(request_url,
                              headers=headers,
                              data=json.dumps(director_query),
                              auth=(director_api_login, director_api_password),
                              verify=False)

        # print(q.text)
        except:
            print("no connection")
            sys.exit(0)
    return q

def director_get_service_apply_id():

    master_host = get_master_host()
    headers = {
        'Accept': 'application/json',
        'X-HTTP-Method-Override': 'GET'
    }

    request_url = "http://"+master_host+"/director/serviceapplyrules"
    try:
        q = requests.get(request_url,
                         headers=headers,
                         data=json.dumps(""),
                         auth=(director_api_login, director_api_password),
                         verify=False)
    except:
        print("no connection")
        sys.exit(0)

    resp_q = json.dumps(q.json(), indent=2)
    resp_dict = json.loads(resp_q)

    last_object = resp_dict["objects"].pop()

    id_list = list()
    for object in resp_dict["objects"]:

        # print(object["id"])
        id_list.append(int(object["id"]))
    if (len(id_list)):
        return max(id_list)
    else:
        return int(last_object["id"])

def getIcingaLocalhostServices():

    hostname = socket.gethostname()
    master_host = get_master_host()
    query = {
        'type': 'Service',
        'host_name': hostname,
        'filter': 'service.vars.opt && service.host.name==\"'+hostname+'\"',
        "joins": [ "host.name", "host.address" ]
    }

    headers = {
        'Accept': 'application/json',
        'X-HTTP-Method-Override': 'GET'
    }

    request_url = "https://"+master_host+":5665/v1/objects/services"

    try:
        r = requests.get(request_url,
                         headers=headers,
                         data=json.dumps(query),
                         auth=(icinga_api_login, icinga_api_password),
                         verify=False)
    except:
        print("no connection")
        sys.exit(0)
    return r

def get_performance_data_from_json(r):

    try:
        resp_str = json.dumps(r.json(), indent=2)
        resp_dict = json.loads(resp_str)
        print(resp_dict)
        results_array = resp_dict['results']
        result = results_array[0]
        data_list = result['attrs']['last_check_result']['performance_data']
        data_str = data_list[0]
        remotes = int(data_str[data_str.find("=")+1:])
        return remotes
    except:
        return 0

def exctractDruServices(r):
    dru_list = []
    resp_str = json.dumps(r.json(), indent=2)
    resp_dict = json.loads(resp_str)
    results_array = resp_dict['results']
    try:
        for result in results_array:
            opt_readed = 0
            if ('vars' in result['attrs']):
                if ('opt' in result['attrs']['vars']):
                    opt_readed = int(result['attrs']['vars']['opt'])
                    dru = int(result['attrs']['vars']['dru'])
                    mac = result['attrs']['vars']['mac']
                    sn = result['attrs']['vars']['sn']
                    name = result["attrs"]["display_name"]
                    dru_list.append(DRU(dru, opt_readed, mac,sn, name))
        return dru_list
    except Exception as e:
        sys.stderr.write("Error - Service list "+str(e)+"\n")
        sys.exit(CRITICAL)

def get_master_host():
    with open(ZONES_CONF) as f:
        datafile = f.readlines()
        for line in datafile:
            if 'host' in line:
                line = (line[line.find("\"")+1:])
                master_host = line[:line.find("\"")]
    return master_host

def get_dru_mac_from_rs485(dru, opt):
    id = str(opt)+str(dru)
    serial = rs485.setSerial('/dev/ttyS1', 9600) 
    query = rs485.obtener_trama(
        'query', 'dru', '00', '00', '4C0B', '09', '000000000000', id)
#    rs485.write_serial_frame(query, serial)
    queries = list()
    queries.append(query)
    rs485.writeSerialQueries(queries,serial)
    hexResponse = rs485.read_serial_frame(serial)
    
    if (hexResponse == None or hexResponse == "" or hexResponse == " " or len(hexResponse) == 0):
        sys.stderr.write("RU"+str(opt)+str(dru)+" - No mac Response\n")
        mac = ''
    else:
        data = rs485.validar_trama_respuesta(hexResponse, 'dru', 4)
        a_bytearray = bytearray(data)
        mac = a_bytearray.hex()
    return mac

def get_dru_sn_from_rs485(dru, opt):
    sn = ''
    port = '/dev/ttyS1'
    baudrate = 9600
    s = serial.Serial(port, baudrate)
    try:
        if port == '/dev/ttyS0':
            baudrate = 19200
        else:
            baudrate = 9600
        #print('baudrate: %d' % baudrate)
        s = serial.Serial(port, baudrate)

        # -- Timeout: 1 seg
        s.timeout = 1

    except serial.SerialException:
        # -- Error al abrir el puerto serie
        sys.stderr.write(
            " Can not open comunication with device")
        sys.exit(2)
    Trama = rs485.obtener_trama(
        'query', 'dru', '00', '00', '0500', '17', '0000000000000000000000000000000000000000', str(opt)+str(dru))
    rs485.write_serial_frame(Trama, s)
    hexResponse = rs485.read_serial_frame(s)

    if (hexResponse == None or hexResponse == "" or hexResponse == " " or len(hexResponse) == 0):
        sys.stderr.write("RU"+str(opt)+str(dru)+" - No sn Response\n")
        mac = ''
    else:
        data = rs485.validar_trama_respuesta(hexResponse, 'dru', 4)
        data_sn = [i for i in data if i != 0]
        a_bytearray = bytearray(data_sn)
        resultHEX = a_bytearray.hex()
        sn = bytearray.fromhex(resultHEX).decode()
    return sn
        
def isValidMACAddress(str):

    # Regex to check valid
    # MAC address
    regex = ("^[0-9A-Fa-f]{12}$")

    # Compile the ReGex
    p = re.compile(regex)

    # If the string is empty
    # return false
    if (str == None):
        return False
    if str == "000000000000":
        return False

    # Return if the string
    # matched the ReGex
    if (re.search(p, str)):
        return True
    else:
        return False

def isValidSN(str):

    # If the string is empty
    # return false
    if (not str):
        return False
    return True

def getConnectedDruQueries(parameters):
    queries = list()
    try:
        for opt in range(1, 5):
            opt_key = 'opt'+str(opt)+'ConnectedRemotes'
            if opt_key in parameters:
                connected_dru_count = int(parameters[opt_key])
                if (connected_dru_count > 0 and connected_dru_count < 8):
                    for dru_found in range(1, connected_dru_count+1):
                        mac = '000000000000'
                        sn = '0000000000000000000000000000000000000000'
                        queries.append(rs485.obtener_trama('query','dru','00','00','094C0B'+mac+'170500'+sn,'22','00',str(opt)+str(dru_found)))
        return queries
    except Exception as e:
        logging.debug("Error - found sn "+ str(e)+"\n")
        return []
    
    
    

if __name__ == "__main__":
    main()
