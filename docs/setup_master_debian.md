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
echo $HOSTNAME > /var/www/html/index.html
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


