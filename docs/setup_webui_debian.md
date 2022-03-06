| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Dependencies

- Install Icinga2 monitor

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

## Complete setup:

Use previous token to login to Icinga Web 2:

open `http://<host-ip>/icingaweb2`

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
