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