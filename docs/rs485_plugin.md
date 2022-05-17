| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# RS485 Check Plugin

## Install plugin

```
mkdir /usr/lib/monitoring-plugins
cp /tmp/sigma-rds/src/plugins/check_rs485.py /usr/lib/monitoring-plugins
cp /tmp/sigma-rds/src/plugins/dmu_check_rs485.py /usr/lib/monitoring-plugins
cp /tmp/sigma-rds/src/plugins/dru_check_rs485.py /usr/lib/monitoring-plugins
cp /tmp/sigma-rds/src/plugins/dru_discovery.py /usr/lib/monitoring-plugins
chmod a+x /usr/lib/monitoring-plugins/check_rs485.py
chmod a+x /usr/lib/monitoring-plugins/dmu_check_rs485.py
chmod a+x /usr/lib/monitoring-plugins/dru_check_rs485.py
chmod a+x /usr/lib/monitoring-plugins/dru_discovery.py
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

## Configure hostname 

```
hostname dmuX

```
add hostname in  `/etc/hostname`


restart service
```
systemctl restart systemd-hostnamed

```
|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
