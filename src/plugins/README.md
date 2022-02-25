## Instalando plugins

`cd /tmp`
`git clone https://gitlab.com/itaum/sigma-rds.git`

`cd sigma-rds/src/plugins`
`cp rs485.py /usr/lib/monitoring-plugins`
`cd /usr/lib/monitoring-plugins`
`chown a+x rs485.py`


## Instalando python

`sudo apk add python3 python3-dev`
`python3 --version`

`python3 -m ensurepip`

`ln -sf python3 /usr/bin/python`


## Instalacion de librerias

`pip install crccheck`
`pip install serial`
`pip install pyserial`


