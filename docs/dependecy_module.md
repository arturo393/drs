# Install Dependency Módule (Master)

```
cd /usr/share/icingaweb2/modules/
git clone https://github.com/visgence/icinga2-dependency-module dependency_plugin
cd dependency_plugin

mkdir -p /etc/icingaweb2/modules/dependency_plugin
```

```
echo -n '[db]
resource = "dependencies"' > /etc/icingaweb2/modules/dependency_plugin/config.ini
```

```
echo -n 'apply Dependency "Parent" for (parent in host.vars.parents) to Host {
      parent_host_name = parent
      assign where host.address && host.vars.parents
} ' > /var/lib/icinga2/api/zones/director-global/director/dependency_apply.conf

```

## Patch module js code:

```
vi +534 /usr/share/icingaweb2/modules/dependency_plugin/public/js/graphManager.js
```

Change

```
if (settings.fullscreen_mode === 'network') {
            window.location.replace("./network?showFullscreen");
        } else {
            window.location.replace("./statusGrid?showFullscreen")
        }
```

by

```
if (settings.fullscreen_mode === 'network') {
            window.location.replace("./dependency_plugin/module/network?showFullscreen");
        } else {
            window.location.replace("./dependency_plugin/module/statusGrid?showFullscreen")
        }
```

## Patch css

Open `/usr/share/icingaweb2/modules/dependency_plugin/public/css/module.less`
Change line `192` from:
`font-size: large;`
to:
`font-size: medium;`

Add line `197`:
`border-radius: 11px;`

## Navigation Item

In Icinga Web 2, add new Navigation item:
Admin->My Account->Navigation->Add

- Name \*: Network Dashboard
- Target: Single Column
- Url: dependency_plugin/module/network?showFullscreen
- Icon: dashboard

Fix the permissions of the module directories:

```
chown -R www-data:icingaweb2 /usr/share/icingaweb2/modules/dependency_plugin
chown -R www-data:icingaweb2 /etc/icingaweb2/modules/dependency_plugin
chown -R nagios:nagios /etc/icinga2/conf.d/
```

mysql

```
CREATE DATABASE dependencies CHARACTER SET 'utf8';
GRANT ALL ON dependencies.* TO dependencies@localhost IDENTIFIED BY 'Admin.123';
```

```
mysql -U dependencies -D dependencies < /usr/share/icingaweb2/modules/dependency_plugin/application/schema/init.sql
```

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

## Add Custom Field to Host Template

Icinga Director > Hosts > Host Templates -> Fields

- Field: parents
- Mandatory: No
