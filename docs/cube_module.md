| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Master: Cube Module

## Installation

```
cd /usr/share/icingaweb2/modules
git clone https://github.com/Icinga/icingaweb2-module-cube cube
chown -R www-data:icingaweb2 cube
sed -i 's/charset = "utf8"/charset = "latin1"/g' /etc/icingaweb2/resources.ini
```

Open ÌcingaWeb2 and go to menu "Configuration" -> "Modules" -> "cube" -> Enable

## Use

Open IcingaWeb2 and go to menú "Reporting" -> "Cube"

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
