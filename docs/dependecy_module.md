# Install Dependency Módule (Master)

```
cd /usr/share/icingaweb2/modules/
<!-- git clone https://github.com/visgence/icinga2-dependency-module dependency_plugin -->
cp -r /tmp/sigma_rds/src/modules/dependency_plugin/ /usr/share/icingaweb2/modules/
cd dependency_plugin

mkdir -p /etc/icingaweb2/modules/dependency_plugin
```

```
echo -n '[db]
resource = "dependencies"' > /etc/icingaweb2/modules/dependency_plugin/config.ini
```

<!--
```
echo -n 'apply Dependency "Parent" for (parent in host.vars.parents) to Host {
      parent_host_name = parent
      assign where host.address && host.vars.parents
} ' > /var/lib/icinga2/api/zones/director-global/director/dependency_apply.conf

``` -->

## Patch default URL

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
 const REDIRECT_URL = 'dependency_plugin/module/hierarchy';
...
```

## Fix the permissions of the module directories:

```
chown -R www-data:icingaweb2 /usr/share/icingaweb2/modules/dependency_plugin
chown -R www-data:icingaweb2 /etc/icingaweb2/modules/dependency_plugin
chown -R nagios:nagios /etc/icinga2/conf.d/
```

## DB Resource

mysql

```
CREATE DATABASE dependencies CHARACTER SET 'utf8';
GRANT ALL ON dependencies.* TO dependencies@localhost IDENTIFIED BY 'Admin.123';
```

```
mysql -U dependencies -D dependencies < /usr/share/icingaweb2/modules/dependency_plugin/application/schema/init.sql
```

## API

```
echo -n 'object ApiUser "dependencies" {
      password = "Admin.123"
      permissions = [ "status/query", "objects/query/*" ]
    }'>> /etc/icinga2/conf.d/api-users.conf
```

systemctl restart icinga2

## Icingaweb2 Dependency Module

### Add DB Resource

Configuration -> Application -> Resources -> Add -> Create a New Resource

- Resource Name: dependencies
- Database Name: dependencies
- Username: dependencies
- Password: Admin.123
- Charset: utf8

### Enable Module

Configuration -> Modules -> Dependency_plugin -> Enable

### Configure Dependency Module

Dependencies -> Settings ->Module Settings

- Database Resource: dependencies
  API Login Information
  - Host: localhost
  - Port: 5665
  - API User: dependencies
  - Password: Admin.123

## Add Custom Data Field

Icinga Director > Define Data Fields

Add a new Data Field

- Field Name: parents
- Caption: Parent Hosts
- Data Type: Array

## Add Custom Service Template

Icinga Director > Service > Service Templates: Add

- Name: rs485_dependency
- Check command: dummy

_Every DMU Port Service should use this template to render detected RDUs_

## Add Custom Field to Host Template (Optional)

Icinga Director > Hosts > Host Templates -> Fields

- Field: parents
- Mandatory: No

---

# Index

- [Readme](/readme.md)
- [Master Node](/docs/setup_master_debian.md)
- [Satellite Node](/docs/setup_satellite_debian.md)
