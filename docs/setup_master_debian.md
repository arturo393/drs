| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Master Node

## Icinga2 Monitor

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

## WebUI

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

echo -e '
<VirtualHost *:80>
  ServerName localhost

  ## Vhost docroot
  # modified for Icinga Web 2
  DocumentRoot "/usr/share/icingaweb2/public"

  ## Rewrite rules
  RewriteEngine On

  <Directory "/usr/share/icingaweb2/public">
      Options SymLinksIfOwnerMatch
      AllowOverride None

      <IfModule mod_authz_core.c>
          # Apache 2.4
          <RequireAll>
              Require all granted
          </RequireAll>
      </IfModule>

      <IfModule !mod_authz_core.c>
          # Apache 2.2
          Order allow,deny
          Allow from all
      </IfModule>

      SetEnv ICINGAWEB_CONFIGDIR "/etc/icingaweb2"

      EnableSendfile Off

      <IfModule mod_rewrite.c>
          RewriteEngine on
          # modified base
          RewriteBase /
          RewriteCond %{REQUEST_FILENAME} -s [OR]
          RewriteCond %{REQUEST_FILENAME} -l [OR]
          RewriteCond %{REQUEST_FILENAME} -d
          RewriteRule ^.*$ - [NC,L]
          RewriteRule ^.*$ index.php [NC,L]
      </IfModule>

      <IfModule !mod_rewrite.c>
          DirectoryIndex error_norewrite.html
          ErrorDocument 404 /error_norewrite.html
      </IfModule>
  </Directory>
</VirtualHost>
' > /etc/apache2/sites-enabled/000-default.conf


```

Restart apache2:
```
systemctl restart apache2
```

### Setup token

```
icingacli setup token create
icingacli setup token show
```

Finish setup:
open `http://<host-ip>/icingaweb2`

## Install and Configure Extra Dependencies

- [Director WebUI Module](/docs/director_module.md)
- [Network Maps WebUI Module](/docs/network_maps_module.md)
- [RS485 Write WebUI Module](/docs/rs485_write_module.md)
- [Graphite WebUI Module](/docs/graphite_module.md)
- [Sigma WebUI Theme](/docs/sigma_theme.md)
- [Cube WebUI Module](/docs/cube_module.md)
- [Base Customizations](/docs/base_customizations.md)
- [Notificaions Customizations](/docs/notificaion_customizations.md)

|                                                                                                                        |
| --------------------------------------------s------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
