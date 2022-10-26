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

    frame_list = list()
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'f8', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'f9', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'fa', '01', '00', '00'))
    frame_list.append(rs485.obtener_trama(
        'query', 'dmu', '07', '00', 'fb', '01', '00', '00'))

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
        sys.exit(2)

    parameter_dict = dict()
    start_time = time.time()
    response_time = 0
    discovery_time = 0
    for frame in frame_list:
        rs485.write_serial_frame(frame, s)
        hex_data_frame = rs485.read_serial_frame(Port, s)
        
        if (hex_data_frame == None or hex_data_frame == "" or hex_data_frame == " "  or len(hex_data_frame) == 0 ):
            sys.stderr.write("No Response")
            fix_frame = rs485.obtener_trama('query','dmu','07','7e','f8','01','00','00')
            rs485.write_serial_frame(fix_frame,s)
            sys.exit(CRITICAL)
        else: 
            data = rs485.validar_trama_respuesta(hex_data_frame,'dmu',0)
            if(data):  
                a_bytearray = bytearray(data)
                hex_validated_frame = a_bytearray.hex()
                cmdNumber = frame[8:10]
                set_parameter_dic_from_validated_frame(
                    parameter_dict, hex_validated_frame, cmdNumber)


    if len(parameter_dict):
        response_time = time.time() - start_time
        parameter_dict["rt"] = str(response_time)
        s.close()
        start_time = time.time()
        discovery_str = dru_discovery(parameter_dict)

        discovery_time = time.time() - start_time
        parameter_dict["rt"] = str(response_time)
        parameter_dict["dt"] = str(discovery_time)

        rt = parameter_dict['rt']
        dt = parameter_dict['dt']
    else:
        rt = "-"
        dt = '-'
        discovery_str = "No Ru detected"
        

    rt_str = "RT="+rt
    rt_str += ";"+str(1)
    rt_str += ";"+str(1)

    dt_str = "DT="+dt
    dt_str += ";"+str(2)
    dt_str += ";"+str(2)
    graphite = rt_str+" "+dt_str

    sys.stderr.write("Summary - "+discovery_str)
    sys.stderr.write("|"+graphite)
    sys.exit(OK)


def set_parameter_dic_from_validated_frame(parameter_dict, hex_validated_frame, cmd_number):
    if cmd_number == 'f8':
        parameter_dict['opt1ConnectedRemotes'] = hex_validated_frame
    elif cmd_number == 'f9':
        parameter_dict['opt2ConnectedRemotes'] = hex_validated_frame
    elif cmd_number == 'fa':
        parameter_dict['opt3ConnectedRemotes'] = hex_validated_frame
    elif cmd_number == 'fb':
        parameter_dict['opt4ConnectedRemotes'] = hex_validated_frame

def dru_compare(found,created):
    if((found.mac == created.mac.swapcase() or found.mac == created.mac ) or (found.sn == created.sn.swapcase() or found.sn == created.sn.swapcase()) ):
        return True
    else:
        return False

def dru_discovery(opt_dict):
    found_dru_list = rs485_get_found_mac_list(opt_dict)
    complete_services = icinga_get_localhost_services()
    new_dru_list = list()
    created_dru_list = list()
    
    detected_str = "detected: " + str(len(found_dru_list))
    if (complete_services.status_code == 200):
        created_dru_list = get_dru_services_list(complete_services, 1)
        
        for found in found_dru_list:
            not_in_created = True
            for created in created_dru_list:
                if (dru_compare(found,created)):
                    if (found.opt != created.opt):
                        ru_created_name = "RU" + \
                            str(created.opt)+str(created.dru)
                        ru_found_name = "RU"+str(found.opt)+str(found.dru)
                        if (len(created.name) > 4):
                            created.name.removesuffix(ru_created_name)
                            name = created.name + "-"+ru_found_name
                        else:
                            name = ru_found_name
                        not_in_new = True
                        for new in new_dru_list:
                            if (new.mac == found.mac):
                                not_in_new = False
                                if (len(name) > 4):
                                    new.name = name
                        if (not_in_new):
                            new_dru_list.append(
                                DRU(found.dru, found.opt, found.mac,found.sn, name))

                        not_in_created = False
                    else:
                        if (found.dru == created.dru):
                            not_in_created = False

            if (not_in_created):
                name = "RU"+str(found.opt)+str(found.dru)
                new_dru_list.append(DRU(found.dru, found.opt, found.mac,found.sn,name))

        for found in found_dru_list:
            not_in_created = True
            for created in created_dru_list:
                if (dru_compare(found,created)):
                    if (found.opt == created.opt):
                        if (found.dru == created.dru):
                            not_in_new = True
                            for new in new_dru_list:
                                if (new.mac == found.mac):
                                    new_dru_list.remove(new)

    dru_host_created = 0
    new_str = " new: " + str(len((new_dru_list)))
    created_str = " created: " + str(len(created_dru_list))
    for dru_service in new_dru_list:
        director_resp = director_create_dru_service(dru_service)
        if (director_resp.status_code == 201):
            dru_host_created += 1

    if dru_host_created > 0:
        director_deploy()
        dru_host_created = 0

    return detected_str+" "+created_str+" "+new_str


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
    opt = service.opt
    dru = service.dru
    mac = service.mac
    name = service.name
    sn = service.sn
    if (dru == 1):
        parent = hostname
    else:
        parent = hostname+"-opt"+str(opt)+"-dru"+str(dru-1)

    director_query = {
        'object_name': name,
        "object_type": "object",
        "host": hostname,
        "imports": ["dmu-dru-working-parameters-service-template"],
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

def icinga_get_localhost_services():

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

def get_dru_services_list(r, opt_asked):
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
        'query', 'dru', '00', '00', '4C0B', '09', '000000000000', str(opt)+str(dru))
    rs485.write_serial_frame(Trama, s)

    hexResponse = rs485.read_serial_frame(port, s)

    if (hexResponse == None or hexResponse == "" or hexResponse == " " or len(hexResponse) == 0):
        sys.stderr.write("RU"+str(opt)+str(dru)+" - No Response\n")
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
    hexResponse = rs485.read_serial_frame(port, s)

    if (hexResponse == None or hexResponse == "" or hexResponse == " " or len(hexResponse) == 0):
        sys.stderr.write("RU"+str(opt)+str(dru)+" - No Response\n")
        sn = ''
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

    # Return if the string
    # matched the ReGex
    if (re.search(p, str)):
        return True
    else:
        return False

def rs485_get_found_mac_list(opt_dict):
    found_dru_list = list()
    try:
        for opt in range(1, 5):
            opt_str = 'opt'+str(opt)+'ConnectedRemotes'
            if(opt_str in opt_dict ):
                dru_connected = int(opt_dict[opt_str])
                if (dru_connected > 0 and dru_connected < 8):
                    for dru_found in range(1, dru_connected+1):
                        mac_found = get_dru_mac_from_rs485(dru_found, opt)
                        time.sleep(0.7)
                        sn_found = get_dru_sn_from_rs485(dru_found,opt)
                        is_valid_mac = isValidMACAddress(mac_found)
                        #sys.stderr.write("mac found: "+mac_found + " valid " + str(isValidstr)+"\r\n")
                        if (is_valid_mac == True):
                            found_dru_list.append(
                                DRU(dru_found, opt, mac_found,sn_found, "new"))


        return found_dru_list
    except Exception as e:
        sys.stderr.write("Error - found sn "+ str(e)+"\n")
        return []


if __name__ == "__main__":
    main()
