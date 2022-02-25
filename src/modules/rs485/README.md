## Module RS485

mysql:

```

CREATE DATABASE rs485;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP, CREATE VIEW, INDEX, EXECUTE ON rs485.* TO admin@localhost IDENTIFIED BY 'Admin.123';

```

console

```
cd /tmp
git clone https://gitlab.com/itaum/sigma-rds.git


cd sigma-rds/src/modules
mysql -p -u root rs485 < rs485/schema/mysql.sql

cp -R rs485 /usr/share/webapps/icingaweb2/modules

cd /usr/share/webapps/icingaweb2/modules
chown -R apache: rs485
```

Enable module http://localhost:8080/icingaweb2/config/modules

Configuration -> Application -> Resources
add rs485_db,
character set to utf8mb4

Configuration -> Modules -> rs485 -> Backend





