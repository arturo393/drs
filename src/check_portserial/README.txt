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