| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# RS485 Write WebUI Module

console

```
apt install icingaweb2-module-ipl
mysql -p -u root director < /tmp/sigma-rds/src/modules/rs485/schema/mysql.sql
cp -R /tmp/sigma-rds/src/modules/rs485 /usr/share/webapps/icingaweb2/modules
chown -R apache:icingaweb2 /tmp/sigma-rds/src/modules/
```

Enable module http://master-host_ip/icingaweb2/config/modules

## WebUI Setup

### create new DB resource

Configuration -> Applications -> Resources -> Create a New Resource

- Resource Name: `rs485_db`

## Set datasource

Configuration -> Modules -> rs485 -> Backend

# Configure remote execution

To allow master node `RS485 write module` to execute commands on satellite node, you need to configure remote execution.

- [Remote Execution](/docs/remote_execution.md)

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
