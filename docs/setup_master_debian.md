# Monitor

```
apt update && apt upgrade
apt install -y icinga2 monitoring-plugins mariadb-server mariadb-client icinga2-ido-mysql git
mariadb-secure-installation
icinga2 feature enable ido-mysql

icinga2 node wizard


```

Change API user password:
`vi /etc/icinga2/conf.d/api-users.conf`

You can verify that the CA public and private keys are stored in the `/var/lib/icinga2/ca` directory

Restart `icinga2`:
`systemctl restart icinga2`

# Web

```
apt install -y apache2 libapache2-mod-php icingacli icingaweb2 icingaweb2-module-director icingaweb2-module-ipl
echo $HOSTNAME > /var/www/html/index.html
a2enmod rewrite

echo -e '
object ApiUser "icingaweb2" {
    password = "Admin.123"
    permissions = [ "status/query", "actions/*", "objects/modify/*", "objects/query/*" ]
}
' >>/etc/icinga2/conf.d/api-users.conf


chown -R www-data:icingaweb2 /etc/icingaweb2/
chown -R www-data:icingaweb2 /usr/share/icingaweb2/



systemctl restart apache2
```

## Setup token

```
icingacli setup token create
icingacli setup token show
```

Finish setup:
open `http://<host-ip>/icingaweb2`
