# Prerequisites

- Admin rights on the host
- Virtual Box
- Vagrant
- Ansible

# Run dev env

`cd vagrant`
`vagrant up`
`vagrant ssh`

# Install

`sudo -i`
`apk update && apk upgrade`

open https://icinga.com/docs/icinga-2/latest/doc/02-installation/

## Install Icinga2

```

apk add icinga2 monitoring-plugins
rc-update add icinga2 default
rc-service icinga2 start

```

## Install IcingaWeb2

### Install MariaDB

```
apk add mariadb mariadb-client

rc-update add mariadb default

/etc/init.d/mariadb setup

rc-service mariadb start

mariadb-secure-installation
enter
Yes
password
Yes
Yes
Yes
Yes

```

### Installing the IDO modules for MySQL and MariaDB

On Alpine Linux the IDO modules for MySQL are included with the icinga2 package and located at `/usr/share/icinga2-ido-mysql/schema/mysql.sql`

### Setting up the MySQL database

```

mysql -u root -p

CREATE DATABASE icinga;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP, CREATE VIEW, INDEX, EXECUTE ON icinga.* TO 'admin'@'localhost' IDENTIFIED BY 'Admin.123';
quit;

```

```

mysql -u root -p icinga < /usr/share/icinga2-ido-mysql/schema/mysql.sql

```

icinga2

### Enabling the IDO MySQL module

`icinga2 feature enable ido-mysql`

edit `/etc/icinga2/features-enabled/ido-mysql.conf`

`rc-service icinga2 restart`

## Webserver

`apk add apache2 php8-apache2`

```

sed -i -e "s/^#LoadModule rewrite_module/LoadModule rewrite_module/" /etc/apache2/httpd.conf
rc-update add apache2 default
rc-service apache2 start

```

## Setting Up Icinga 2 REST API

`icinga2 api setup`

add the follow object to the file `/etc/icinga2/conf.d/api-users.conf`

```

object ApiUser "icingaweb2" {
password = "Wijsn8Z9eRs5E25d"
permissions = [ "status/query", "actions/*", "objects/modify/*", "objects/query/*" ]
}

```

## Enabling Modules

```

icinga2 feature enable notification
icinga2 feature enable checker
icinga2 feature enable mainlog
icinga2 feature enable icingadb

```

## Post installs

`rc-service icinga2 restart`

## Installing Icinga Web 2

`apk add icingaweb2 icingaweb2-doc icingaweb2-bash-completion`

```

icingacli setup token create
icingacli setup token show
chown -R apache: /etc/icingaweb2
chown -R apache: /var/lib/icingaweb2

```

### Configuring Icinga Web 2

mysql

```

CREATE DATABASE icingaweb2;

GRANT ALL ON icingaweb2.* TO icingaweb2@localhost IDENTIFIED BY 'Admin.123';

quit;

```

console

```

icingacli setup config webserver apache --document-root /usr/share/webapps/icingaweb2/public > /etc/apache2/conf.d/icingaweb2.conf

chown -R apache: /usr/share/webapps/icingaweb2/

rc-service apache2 restart

```

# Post Install/Setup

visit http://localhost:8080/icingaweb2/setup and complete setup

---

# Extra Modules

`cd /usr/share/webapps/icingaweb2/modules`

Enable module http://localhost:8080/icingaweb2/config/modules

### Incubator

```

apk add icingaweb2-module-incubator-doc icingaweb2-module-incubator

```

### Director

console
`apk add icingaweb2-module-director icinga-director-openrc icingaweb2-module-director-doc`

mysql

```
CREATE DATABASE director CHARACTER SET 'utf8';
CREATE USER director@localhost IDENTIFIED BY 'Admin.123';
GRANT ALL ON director.* TO director@localhost;
```

console:

```
icingacli module enable director

grep NodeName /etc/icinga2/constants.conf
```

Add new resource: http://localhost:8080/icingaweb2/config/resource

console:

```
rc-update add icinga-director default
rc-service icinga-director start
```

console

```
apk add git
cd /usr/share/webapps/icingaweb2/modules
```

## PDF Export

```
cd /usr/share/webapps/icingaweb2/modules
apk add dbus dbus-openrc
rc-update add dbus default
apk add chromium chromium-swiftshader chromium-chromedriver mesa-osmesa mesa-dev font-noto-gothic php8-fileinfo
apk add ttf-freefont font-noto-emoji
apk add wait4ports zlib-dev dhclient
git clone https://github.com/Icinga/icingaweb2-module-pdfexport.git pdfexport
```

## Reporting

`git clone https://github.com/Icinga/icingaweb2-module-reporting.git reporting`

mysql:

```

CREATE DATABASE reporting;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP, CREATE VIEW, INDEX, EXECUTE ON reporting.* TO reporting@localhost IDENTIFIED BY 'Admin.123';

```

console

```
cd /usr/share/webapps/icingaweb2/modules
cd reporting
mysql -p -u root reporting < schema/mysql.sql

```

Configuration -> Application -> Resources
add reporting,
character set to utf8mb4

Configuration -> Modules -> reporting -> Backend

### RC Reporting Service

```

#!/sbin/openrc-run

name=$RC_SVCNAME
command="/usr/bin/icingacli"
command_args="reporting schedule run"
supervisor="supervise-daemon"

```

```

chmod a+x /etc/init.d/icinga-reporting
rc-update add icinga-reporting default
rc-service icinga-reporting start

```

## Manubulon SNMP Plugins

```

apk add perl perl-net-snmp perl-getopt-long perl-crypt-des perl-crypt-rijndael perl-digest-hmac

cd /tmp
git clone https://github.com/SteScho/manubulon-snmp.git
cd manubulon-snmp

install -o root -g root -m755 plugins/*.pl /usr/lib/monitoring-plugins

echo 'const ManubulonSnmpCommunity = "icingasnmpro"' >> /etc/icinga2/constants.conf

```

Service Template -> Service
Host Template -> Host

`apk add nagios-plugins-all`

## Modbus plugin

```

cd /tmp
git clone https://github.com/AndreySV/check_modbus.git
cd check_modbus/
apk add automake autoconf make gcc libmodbus libmodbus-dev gccmakedep gc libgc++ libstdc++6 gcc-objc

./autogen.sh
./configure --prefix=/usr/lib/monitoring-plugins
make
cp src/check_modbus /usr/lib/monitoring-plugins

```

# Web Modules development

https://github.com/Icinga/icingaweb2-module-training/blob/master/doc/extending-icinga-web-2.md#your-own-module-in-the-web-frontend

# Install Graphite

## Dependencies

```
apk add python3 python3-dev py-pip
ln -s /usr/bin/python3 /usr/bin/python
apk add py3-cairo cairo-dev
pip install django python-memcached django-tagging twisted txAMQP
```

## Graphite web

```
git clone --depth 1 https://github.com/graphite-project/graphite-web.git /opt/graphite-web
cd /opt/graphite-web
python ./setup.py install
```

## Whisper

```
git clone --depth 1 https://github.com/graphite-project/whisper.git /opt/whisper
cd /opt/whisper
python ./setup.py install
```

## Carbon

```
git clone --depth 1 https://github.com/graphite-project/carbon.git /opt/carbon
cd /opt/carbon
python ./setup.py install
```

## Statsd

```
git clone https://github.com/etsy/statsd.git /opt/statsd
```

## Graphite-web configuration

```
cd /opt/graphite/conf

```
