| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Install Network Map WebUI Module (Only Master)

Use the module provided by this repository:

```
cp -r /tmp/sigma-rds/src/modules/network_maps/ /usr/share/icingaweb2/modules/
mkdir -p /etc/icingaweb2/modules/network_maps
```

```
echo -n '[db]
resource = "dependencies"' > /etc/icingaweb2/modules/network_maps/config.ini
```

## Patch WebUI default URL

Edit `/usr/share/icingaweb2/application/forms/Authentication/LoginForm.php` and change `line 24`:

from:

```
...
 const REDIRECT_URL = 'dasboard';
...
```

to:

```
...
 const REDIRECT_URL = 'network_maps/module/hierarchy';
...
```

## Fix the permissions of the module directories:

```
chown -R www-data:icingaweb2 /usr/share/icingaweb2/modules/network_maps
chown -R www-data:icingaweb2 /etc/icingaweb2/modules/network_maps
chown -R nagios:nagios /etc/icinga2/conf.d/
```

## Add new DB Resource

mysql

```
CREATE DATABASE dependencies CHARACTER SET 'utf8';
GRANT ALL ON dependencies.* TO dependencies@localhost IDENTIFIED BY 'Admin.123';
```

```
mysql -U dependencies -D dependencies < /usr/share/icingaweb2/modules/network_maps/application/schema/init.sql
```

## Add API user

```
echo -n 'object ApiUser "dependencies" {
      password = "Admin.123"
      permissions = [ "status/query", "objects/query/*" ]
    }'>> /etc/icinga2/conf.d/api-users.conf
```

## Restart monitor process:

`systemctl restart icinga2`

## Icingaweb2 Dependency Module

### Add DB Resource

Configuration -> Application -> Resources -> Add -> Create a New Resource

- Resource Name: dependencies
- Database Name: dependencies
- Username: dependencies
- Password: Admin.123
- Charset: utf8

### Enable Module

Configuration -> Modules -> Network_Maps -> Enable

### Configure Dependency Module

Network_Maps -> Settings ->Module Settings

- Database Resource: dependencies
  API Login Information
  - Host: localhost
  - Port: 5665
  - API User: dependencies
  - Password: Admin.123

### Add Custom Data Fields

Icinga Director > Define Data Fields

Add a new Data Field

- Field Name: parents
- Caption: Parent Hosts
- Data Type: Array

Add a second Data Field

- Field Name: isDMUPort
- Caption: If is a DMU Port That Connects RDUs
- Data Type: Boolean

### Add Data Field to a Service Template

Icinga Director > Service > Service Templates > Fields

- Field: `isDMUPort`
- Mandatory: `Optional`

_Every DMU Port Service should use this Data Field to render detected RDUs_

## Enable Custom Data Field to DMU Port Service (Optional)

Icinga Director > Seervices > Service -> Custom Properties

- isDMUPort: Yes

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
