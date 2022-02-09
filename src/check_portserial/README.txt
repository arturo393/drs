Instalando python
===========================

sudo apk add python3 python3-dev
python3 --version

python3 -m ensurepip

ln -sf python3 /usr/bin/python


Instalando EMULADOR puerta serial
====================================
apk add socat

ej. comando
socat -d -d pty,raw,echo=0 pty,raw,echo=0


https://www.tutorialspoint.com/python/python_command_line_arguments.htm


python check_portserial.py --port=/dev/ttyS3 --action=03 --i=07 --cmdNumber=F8 --cmdBodyLenght=02 --cmdData=0 --crc=B282
python check_portserial.py --port=/dev/pts/2 --action=03 --i=07 --cmdNumber=F8 --cmdBodyLenght=02 --cmdData=0 --crc=B282

python -m serial.tools.list_ports


opciones:
    -p, --port=  PORT o DEVICE: Puerto serie a leer o escribir Ej. /dev/ttyS0
    -a, --action= ACTION: read = Query ; write = Set o write
    -i, --dmuId= INTERFACE: ID de PA Ã³ DSP, Ej. 0x07 => DSP , 0x08 => PA, En la trama MODULE_ADDRESS_FUNCTION
    -d, --druId= DIVICE: DRU ID number, En la trama MODULE_ADDRESS_FUNCTION
    -n, --cmdNumber= CMDNUMBER: Comando a enviar
    -l, --cmdBodyLenght= CMDBODYLENGHT: Indentica si lee o escribe
    -c, --cmdData= CMDDATA: dato a escribir


    Ejemplo:
    check_portserial.py -p COM0       --> Usar el primer puerto serie (Windows)
    check_portserial.py -p /dev/ttyS0 --> Especificar el dispositivo serie (Linux)

python check_portserial.py --port=/dev/ttyS2 --action=write --dmuId=0x07  --druId=00 --cmdNumber=F8 --cmdBodyLenght=2 --cmdData=0x3801
python check_portserial.py --port=/dev/ttyS2 --action=write --dmuId=0x07  --druId=00 --cmdNumber=F8 --cmdBodyLenght=3 --cmdData=0x3801