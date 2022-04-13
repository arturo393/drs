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
from crccheck.crc import Crc16Xmodem
import argparse
# importing the requests library
import requests,json
import socket
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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


ZONES_CONF = '/etc/icinga2/zones.conf'
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
    master_host = get_master_host()
    
    hostname = socket.gethostname()    
    ip_addr=socket.gethostbyname(hostname)

    servicename = hostname+'!'+opt
    
    icinga_query = {
            'type': 'Service',
            'service':servicename,
            'filter': 'service.state == ServiceOK',
            'attrs': ['last_check_result']
            }

    r = http_get_query(master_host, icinga_query)

    if (r.status_code == 200):
        remotes = get_performance_data(r)
        dru_list = list()
        for remote in range(remotes):
            dru_list.append("dru"+str(remote+1))

    
    remotes_created = 0
    for dru in dru_list:
        
        director_query = {
            'object_name':hostname+"-"+opt+"-"+dru, 
            "object_type": "object",
            "address": ip_addr ,
            "imports": ["dmu-"+opt+"-"+dru+"-host-template"],
            "display_name": "Remote "+ dru[3:],
            "zone": hostname
            
        }
        
        q = http_post_director(master_host, director_query)

        resp_str=json.dumps(q.json(),indent=2)
        resp_dict = json.loads(resp_str)
        if 'address' in resp_dict:
            remotes_created += 1
            
    if(remotes_created > 0):
        http_post_deploy(master_host)
        

    sys.exit(0)
            
def http_post_deploy(master_host):
    director_api_login = "admin"
    director_api_password ="Admin.123"
    
    director_url = "http://"+master_host+"/director/config/deploy"
    director_headers = {
        'Accept':'application/json',
        'X-HTTP-Method-Override': 'POST'
        }
    
    q = requests.post(director_url,
                         headers=director_headers,
                         auth=(director_api_login,director_api_password),
                         verify=False)
                     
    return q

def http_post_director(master_host, director_query):
    director_api_login = "admin"
    director_api_password ="Admin.123"
    
    director_url = "http://"+master_host+"/director/host"
    director_headers = {
        'Accept':'application/json',
        'X-HTTP-Method-Override': 'POST'
        }
    
    q = requests.post(director_url,
                         headers=director_headers,
                         data=json.dumps(director_query),
                         auth=(director_api_login,director_api_password),
                         verify=False)
                     
    return q

def http_get_query(master_host, icinga_query):
    icinga_headers = {
        'Accept':'application/json',
        'X-HTTP-Method-Override': 'GET'
    }
    
    request_url = "https://"+master_host+":5665/v1/objects/services"
    api_login = "root"
    api_password ="Admin.123"
    r = requests.get(request_url,
                     headers=icinga_headers,
                     data=json.dumps(icinga_query),
                     auth=(api_login,api_password),
                     verify=False)
                     
    return r

def get_performance_data(r):
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