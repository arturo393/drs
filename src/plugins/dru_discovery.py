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
import check_rs485 as rs485

urllib3.disable_warnings()
# --------------------------------
# -- Declaracion de constantes
# --------------------------------
class DRU:
    def __init__(self, dru, opt, mac, name):
        self.dru = dru
        self.opt = opt
        self.mac = mac
        self.name = name
OK =  0
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
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','f8','01','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','f9','01','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','fa','01','00','00'))
    frame_list.append(rs485.obtener_trama('query','dmu','07','00','fb','01','00','00'))
    
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
        rs485.write_serial_frame(frame,s)
        hex_data_frame = rs485.read_serial_frame(Port, s)

        data = rs485.validar_trama_respuesta(hex_data_frame,'dmu',0)
        a_bytearray = bytearray(data)
        hex_validated_frame = a_bytearray.hex()
        try:
              resultOK =  int(hex_validated_frame, 16)
        except:
            print("No Response")
            sys.exit(2)

        cmdNumber = frame[8:10]

        set_parameter_dic_from_validated_frame(parameter_dict, hex_validated_frame, cmdNumber)
        

    


    response_time = time.time() - start_time
    parameter_dict["rt"] = str(response_time)
    s.close()    
     
    start_time = time.time()
    dru_created = dru_discovery(parameter_dict)
    
    discovery_time = time.time() - start_time
    parameter_dict["rt"] = str(response_time)
    parameter_dict["dt"] = str(discovery_time)
    
    rt = parameter_dict['rt']
    
    rt_str  ="RT="+rt
    rt_str +=";"+str(1)
    rt_str +=";"+str(1)

    dt_str ="DT="+parameter_dict['dt']
    dt_str +=";"+str(2)
    dt_str +=";"+str(2)
    graphite = rt_str+" "+dt_str

    sys.stderr.write(str(dru_created)+" RU Found")
    sys.stderr.write("|"+graphite)
    sys.exit(OK)
    
def set_parameter_dic_from_validated_frame(parameter_dict, hex_validated_frame, cmd_number):
    if cmd_number=='f8':
        parameter_dict['opt1ConnectedRemotes'] = hex_validated_frame
    elif cmd_number=='f9':
        parameter_dict['opt2ConnectedRemotes'] = hex_validated_frame
    elif cmd_number=='fa':
        parameter_dict['opt3ConnectedRemotes'] = hex_validated_frame
    elif cmd_number=='fb':
        parameter_dict['opt4ConnectedRemotes'] = hex_validated_frame

def dru_discovery(opt_dict):
    found_dru_list = rs485_get_found_mac_list(opt_dict)
    complete_services = icinga_get_localhost_services()
    new_dru_list = list()

    if (complete_services.status_code == 200):
        created_dru_list = get_dru_services_list(complete_services, 1)          
        for found in found_dru_list:
            not_in_created = True
            for created in created_dru_list:
                if (found.mac == created.mac.swapcase() or found.mac == created.mac):                
                    if (found.opt != created.opt):
                        ru_created_name = "RU"+str(created.opt)+str(created.dru)
                        ru_found_name = "RU"+str(found.opt)+str(found.dru)                       
                        if(len(created.name) > 4):
                            created.name.removesuffix(ru_created_name)
                            name = created.name +"-"+ru_found_name
                        else:
                            name = ru_found_name
                        not_in_new = True
                        for new in new_dru_list:
                            if(new.mac == found.mac):
                                not_in_new = False
                                if(len(name) > 4):
                                    new.name = name                                  
                        if(not_in_new):
                            new_dru_list.append(
                            DRU(found.dru, found.opt, found.mac,name))
                        
                        not_in_created = False
                    else:
                      if(found.dru == created.dru):
                        not_in_created = False
  
            if(not_in_created):
                name = "RU"+str(found.opt)+str(found.dru)
                new_dru_list.append(DRU(found.dru, found.opt, found.mac,name))
     
        
        for found in found_dru_list:
            not_in_created = True
            for created in created_dru_list:
                if (found.mac == created.mac.swapcase() or found.mac == created.mac):
                    if (found.opt == created.opt):
                        if(found.dru == created.dru):
                            not_in_new = True
                            for new in new_dru_list:
                                if(new.mac == found.mac):
                                    new_dru_list.remove(new)
                           
    dru_host_created = 0
    for dru_service in new_dru_list:
        director_resp = director_create_dru_service(dru_service)
        if (director_resp.status_code == 201):
            dru_host_created += 1

    if dru_host_created > 0:
        director_deploy()
        dru_host_created = 0
        
    return dru_host_created

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
    # print(resp_dict)
    results_array = resp_dict['results']
    try:
        for result in results_array:
            opt_readed = 0
            if ('opt' in result['attrs']['vars']):
                opt_readed = int(result['attrs']['vars']['opt'])
          #  if (opt_asked == opt_readed):
                dru = int(result['attrs']['vars']['dru'])
                mac = result['attrs']['vars']['mac']
                name = result["attrs"]["display_name"]
                dru_list.append(DRU(dru, opt_readed, mac, name))
        return dru_list
    except Exception as e:
        return []

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

    data = rs485.validar_trama_respuesta(hexResponse, 'dru', 4)
    a_bytearray = bytearray(data)
    mac = a_bytearray.hex()
    return mac

def rs485_get_found_mac_list(opt_dict):
    found_dru_list = list()
    for opt in range(1, 5):
        dru_connected = int(opt_dict['opt'+str(opt)+'ConnectedRemotes'])
        if (dru_connected > 0 and dru_connected < 8):
            for dru_found in range(1, dru_connected+1):
                mac_found = get_dru_mac_from_rs485(dru_found, opt)
                found_dru_list.append(DRU(dru_found, opt, mac_found, "new"))

    return found_dru_list


if __name__ == "__main__":
    main()
