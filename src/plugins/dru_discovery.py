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

from pickle import FALSE, TRUE
import sys
import getopt
import serial
import time
from crccheck.crc import Crc16Xmodem
import argparse
# importing the requests library
import requests,json
import socket
import urllib3
urllib3.disable_warnings()
# --------------------------------
# -- Declaracion de constantes
# --------------------------------
ZONES_CONF = '/etc/icinga2/zones.conf'
    
director_api_login = "admin"
director_api_password ="Admin.123"

icinga_api_login = "root"
icinga_api_password ="Admin.123"
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

def analizar_argumentos():

    # Construct the argument parser
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    #ap.add_argument("-h", "--help", required=False,  help="help")
    ap.add_argument("-o", "--opt", required=True,  help="opt es requerido", )


    try:
        args = vars(ap.parse_args())
    except getopt.GetoptError as e:
        # print help information and exit:
        print(e.msg)
        help()
        sys.exit(1)

    opt = str(args['opt'])

    if opt == "":
        sys.stderr.write("CRITICAL - El puerto es obligatorio\n")
        sys.exit(2)

    return opt

# ----------------------
#   MAIN
# ----------------------
    
def main():
    
    opt = analizar_argumentos()
    
    r = icinga_get_service_last_check_result(opt)
    dru_list = list()
    #print(r)
    if (r.status_code == 200):
        remotes = get_performance_data_from_json(r)
        for remote in range(remotes):
            dru_list.append("dru"+str(remote+1))
   # id = director_get_service_apply_id()
    remotes_created = 0
      
    #print(dru_list)
    for dru in dru_list:
        q = director_create_dru_service(opt,dru)       

        if 'address' in resp_dict:
#            director_create_dru_services(opt, dru)
            remotes_created += 1
            
    if(remotes_created > 0):
        director_deploy()
    
    
    sys.exit(0)
            
def director_deploy():
    master_host = get_master_host()  
    director_url = "http://"+master_host+"/director/config/deploy"
    director_headers = {
        'Accept':'application/json',
        'X-HTTP-Method-Override': 'POST'
        }
    
    try: 
        q = requests.post(director_url,
                         headers=director_headers,
                         auth=(director_api_login,director_api_password),
                         verify=False)
    except:
        print("no connection")
        sys.exit(0)

    return q


def director_create_dru_host(opt,dru):
    
    hostname = socket.gethostname()    
    ip_addr=socket.gethostbyname(hostname)
    master_host = get_master_host()

    if(dru == "dru1"):
        parent = hostname
    else:
        druid = int(dru[3:]) - 1
        parent = hostname+"-"+opt+"-dru"+str(druid)
    
    director_query = {
            'object_name':hostname+"-"+opt+"-"+dru, 
            "object_type": "object",
            "zone":hostname,
            "address": ip_addr ,
            "imports": ["dmu-opt-dru-host-template"],
            "display_name": "Remote "+ dru[3:]+"("+opt+")",
             "vars": {
              "opt": opt[3:],
              "dru": dru[3:],
              "parents": [ parent ]     
              }
        }
        
   
    request_url = "http://"+master_host+"/director/host"
    headers = {
        'Accept':'application/json',
        'X-HTTP-Method-Override': 'POST'
        }
    
    try:
        q = requests.post(request_url,
                         headers=headers,
                         data=json.dumps(director_query),
                         auth=(director_api_login,director_api_password),
                         verify=False)
       
    except:
        print("no connection")
        sys.exit(0)

    #print(json.dumps(q.json(),indent=2))
    return q
    
def director_create_dru_service(opt,dru):
    
    hostname = socket.gethostname()    
    ip_addr=socket.gethostbyname(hostname)
    master_host = get_master_host()

    if(dru == "dru1"):
        parent = hostname
    else:
        druid = int(dru[3:]) - 1
        parent = hostname+"-"+opt+"-dru"+str(druid)
    
    director_query = {

            'object_name':hostname+"-"+opt+"-"+dru, 
            "object_type": "object",
            "host": hostname,
            "imports": ["dmu-dru-working-parameters-service-template"],
            "display_name": "Remote "+ dru[3:]+"("+opt+")",
             "vars": {
              "opt": opt[3:],
              "dru": dru[3:],
              "parents": [ parent ]     
              }
        }
        
   
    request_url = "http://"+master_host+"/director/service"
    headers = {
        'Accept':'application/json',
        'X-HTTP-Method-Override': 'POST'
        }
    
    try:
        q = requests.post(request_url,
                         headers=headers,
                         data=json.dumps(director_query),
                         auth=(director_api_login,director_api_password),
                         verify=False)
       
    except:
        print("no connection")
        sys.exit(0)

    #print(json.dumps(q.json(),indent=2))
    return q

def director_create_dru_applyservices(opt, dru):

    service_name = "dlPower-2"
    master_hostname = socket.gethostname()
    master_host = get_master_host()
    remote_hostname = master_hostname+"-opt"+opt[3:]+"-dru"+dru[3:]
    imports = list()
     
     ## the names are from service templates
    imports.append(("Downlink Power","dlPower"))
    imports.append(("Uplink Power","ulPower"))
    imports.append(("Power Amplifier Temperature","paTemperature"))
    imports.append(("VSWR","vswr"))   
    
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
        
        #print(q.text)
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

    resp_q = json.dumps(q.json(),indent=2)
    resp_dict = json.loads(resp_q)

    last_object=resp_dict["objects"].pop()
    
    id_list = list()
    for object in resp_dict["objects"]:
      
      #print(object["id"])
      id_list.append(int(object["id"]))
    if(len(id_list)):
      return max(id_list)
    else:
      return int(last_object["id"])


def icinga_get_service_last_check_result(opt):
    
    hostname = socket.gethostname()    
    servicename = hostname+'!'+opt
    master_host = get_master_host()

    query = {
            'type': 'Service',
            'service':servicename,
            'filter': 'service.state == ServiceOK',
    #        'attrs': ['last_check_result']
            }
        
    headers = {
        'Accept':'application/json',
        'X-HTTP-Method-Override': 'GET'
    }
    
    request_url = "https://"+master_host+":5665/v1/objects/services"

    try:
        r = requests.get(request_url,
                     headers=headers,
                     data=json.dumps(query),
                     auth=(icinga_api_login,icinga_api_password),
                     verify=False)
    except:
        print("no connection")
        sys.exit(0)
    return r




def get_performance_data_from_json(r):
    try:
        resp_str=json.dumps(r.json(),indent=2)
        resp_dict = json.loads(resp_str)
        results_array = resp_dict['results']
        result = results_array[0]
        data_list = result['attrs']['last_check_result']['performance_data']
        data_str = data_list[0]
        remotes = int(data_str[data_str.find("=")+1:])
        return remotes
    except:
        return 0

def get_master_host():
    with open(ZONES_CONF) as f: 
        datafile = f.readlines()
        for line in datafile:
            if 'host' in line:
                line=(line[line.find("\"")+1:])
                master_host=line[:line.find("\"")]
    return master_host

            
if __name__ == "__main__":
    main()
