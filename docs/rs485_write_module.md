## Module RS485

console

```
cd /tmp
git clone https://gitlab.com/itaum/sigma-rds.git


cd sigma-rds/src/modules
mysql -p -u root director < rs485/schema/mysql.sql

cp -R rs485 /usr/share/webapps/icingaweb2/modules

cd /usr/share/webapps/icingaweb2/modules
chown -R apache: rs485

apt install icingaweb2-module-ipl
```

Enable module http://localhost:8080/icingaweb2/config/modules

check datasource module director

Configuration -> Modules -> rs485 -> Backend

---

# Index

- [Readme](/readme.md)
- [Master Node](/docs/setup_master_debian.md)
- [Satellite Node](/docs/setup_satellite_debian.md)
