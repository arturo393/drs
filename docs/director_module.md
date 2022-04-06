| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Master: Director Module

```
apt install -y icingaweb2-module-director
```

mysql

```
CREATE DATABASE director CHARACTER SET 'utf8';
CREATE USER director@localhost IDENTIFIED BY 'Admin.123';
GRANT ALL ON director.* TO director@localhost;
```

open `http://<host-ip>/icingaweb2`
Go to menu "Configuration" -> "Application" -> "Resources" -> "Add" -> "Create a New Resource"

```
Resource Name: director_db
Database Name: director
Username: director
Password: Admin.123
Charset: utf8
```

Go to menu "Icinga Director" -> "[Create Schema]"


# Upgrade Director

To upgrade director module, follow the steps following the steps in the [upgrade_director.md](/docs/upgrade_director.md) file.

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
