# Monitor

```
apt update && apt upgrade
apt install icinga2 monitoring-plugins
apt install mariadb-server mariadb-client
mariadb-secure-installation
apt install icinga2-ido-mysql
icinga2 feature enable ido-mysql

icinga2 node wizard
/etc/init.d/icinga2 restart

```

Change API user password:
`vi /etc/icinga2/conf.d/api-users.conf`

You can verify that the CA public and private keys are stored in the `/var/lib/icinga2/ca` directory

# Web

```
apt install apache2 libapache2-mod-php icingacli icingaweb2 icingaweb2-module-director
echo "." > /var/www/html/index.html
a2enmod rewrite

echo -e '
object ApiUser "icingaweb2" {
    password = "Admin.123"
    permissions = [ "status/query", "actions/*", "objects/modify/*", "objects/query/*" ]
}
' >>/etc/icinga2/conf.d/api-users.conf

systemctl restart apache2
```

## Setup token

```
icingacli setup token create
icingacli setup token show
```

open `http://<host-ip>/icingaweb2`

```
chown -R www-data:icingaweb2 /etc/icingaweb2/
chown -R www-data:icingaweb2 /usr/share/icingaweb2/

```

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

## Graphite

### Install Graphite

`apt-get install graphite-web graphite-carbon git -y`

### Enable Icinga2 Feature

```
icinga2 feature enable graphite
vi /etc/icinga2/features-enabled/graphite.conf

echo -e 'object GraphiteWriter "graphite" {
  host = "127.0.0.1"
  port = 2003
}' > /etc/icinga2/features-enabled/graphite.conf

systemctl restart icinga2
```

### Install Graphite Icingaweb2 Module

```
cd /usr/share/icingaweb2/modules/
git clone https://github.com/Icinga/icingaweb2-module-graphite graphite
cd graphite
chown -R apache: .
```
