## Instalación de plugin


```
cd /tmp
git clone https://gitlab.com/itaum/sigma-rds.git
cd sigma-rds
mkdir /usr/lib/monitoring-plugins
cp src/plugins/check_rs485.py /usr/lib/monitoring-plugins
cd /usr/lib/monitoring-plugins
chmod a+x check_rs485.py
```

## Instalando python

```
apt install python3 python3-dev python3-pip
python3 --version
ln -sf python3 /usr/bin/python
ln -sf pip3 /usr/bin/pip
```
## Instalacion de librerias

```
pip install crccheck serial pyserial
```


