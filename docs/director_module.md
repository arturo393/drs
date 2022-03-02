# Master

## Director

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
