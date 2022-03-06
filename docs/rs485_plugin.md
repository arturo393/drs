# RS485 Check Plugin

## Install plugin

```
mkdir /usr/lib/monitoring-plugins
cp /tmp/src/sigma-rds/plugins/check_rs485.py /usr/lib/monitoring-plugins
chmod a+x /usr/lib/monitoring-plugins/check_rs485.py
```

## Install python

```
apt install python3 python3-dev python3-pip
ln -sf python3 /usr/bin/python
ln -sf pip3 /usr/bin/pip
```

## Install python libs

```
pip install crccheck serial pyserial
```

---

# Index

- [Readme](/readme.md)
- [Master Node](/docs/setup_master_debian.md)
- [Satellite Node](/docs/setup_satellite_debian.md)
