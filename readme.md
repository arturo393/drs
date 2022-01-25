# Run dev env

`cd vagrant`
`vagrant up`
`vagrant ssh`

# Install

`apk update && apk upgrade`

open https://icinga.com/docs/icinga-2/latest/doc/02-installation/

## Install Icinga2

`apk add icinga2 monitoring-plugins`
`rc-update add icinga2 default`
`rc-service icinga2 start`

## Install IcingaWeb2

### Install MariaDB

`apk add mariadb mariadb-client`
`rc-update add mariadb default`
`mariadb-secure-installation`
`rc-service mariadb start`

### Installing the IDO modules for MySQL and MariaDB

On Alpine Linux the IDO modules for MySQL are included with the icinga2 package and located at `/usr/share/icinga2-ido-mysql/schema/mysql.sql`

### Setting up the MySQL database

```
mysql -u root -p

CREATE DATABASE icinga;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP, CREATE VIEW, INDEX, EXECUTE ON icinga.* TO 'admin'@'localhost' IDENTIFIED BY 'Admin.123';
quit
```

```
mysql -u root -p icinga < /usr/share/icinga2-ido-mysql/schema/mysql.sql
```

ediit `/etc/icinga2/features-enabled/ido-mysql.conf`

### Enabling the IDO MySQL module

`icinga2 feature enable ido-mysql`
`rc-service icinga2 restart`

## Webserver

`apk add apache2 php8-apache2`

```
sed -i -e "s/^#LoadModule rewrite_module/LoadModule rewrite_module/" /etc/apache2/httpd.conf
rc-update add apache2 default
rc-service apache2 start
```

## Setting Up Icinga 2 REST API

```
icinga2 api setup
```

`vim /etc/icinga2/conf.d/api-users.conf`

```
object ApiUser "icingaweb2" {
  password = "Wijsn8Z9eRs5E25d"
  permissions = [ "status/query", "actions/*", "objects/modify/*", "objects/query/*" ]
}
```

## Enabling Modules

`icinga2 feature enable notification`
`icinga2 feature enable checker`
`icinga2 feature enable mainlog`
`icinga2 feature enable icingadb`

## Post installs

`rc-service icinga2 restart`

## Installing Icinga Web 2

`apk add icingaweb2 icingaweb2-doc icingaweb2-bash-completion`

`icingacli setup token create`
`icingacli setup token show`
`chown -R apache: /etc/icingaweb2`
`chown -R apache: /var/lib/icingaweb2`

### Configuring Icinga Web 2

```
CREATE DATABASE icingaweb2;

GRANT ALL ON icingaweb2.* TO icingaweb2@localhost IDENTIFIED BY 'CHANGEME';
```

`icingacli setup config webserver apache --document-root /usr/share/webapps/icingaweb2/public > /etc/apache2/conf.d/icingaweb2.conf`

`chown -R apache: /usr/share/webapps/icingaweb2/`

`rc-service apache2 restart`

### Incubator

```
apk add icingaweb2-module-incubator-doc icingaweb2-module-incubator

```

### Director

`apk add icingaweb2-module-director icinga-director-openrc icingaweb2-module-director-doc`

`CREATE DATABASE director CHARACTER SET 'utf8';`
`CREATE USER director@localhost IDENTIFIED BY 'Admin.123';`
`GRANT ALL ON director.* TO director@localhost;`

`icingacli module enable director`

`grep NodeName /etc/icinga2/constants.conf`

`http://localhost:8080/icingaweb2/config/resource`

`rc-update add icinga-director default`
`rc-service icinga-director start`

# Post Install/Setup

```
http://localhost:8080/icingaweb2/setup
```

---

# Extra Modules

`apk add git`
`cd /usr/share/webapps/icingaweb2/modules`

http://localhost:8080/icingaweb2/config/modules

## PDF Export

`apk add dbus dbus-openrc`
`rc-update add dbus default`

`apk add chromium chromium-swiftshader chromium-chromedriver mesa-osmesa mesa-dev font-noto-gothic php8-fileinfo`
`apk add ttf-freefont font-noto-emoji`
`apk add wait4ports zlib-dev dhclient`
`git clone https://github.com/Icinga/icingaweb2-module-pdfexport.git pdfexport`

## Reporting

`git clone https://github.com/Icinga/icingaweb2-module-reporting.git reporting`

```
CREATE DATABASE reporting;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP, CREATE VIEW, INDEX, EXECUTE ON reporting.* TO reporting@localhost IDENTIFIED BY 'Admin.123';
```

```
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
