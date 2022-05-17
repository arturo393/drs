| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |


# Backup DB

```
cd /opt
mysqldump --host=localhost --user=root --port=3306 -p --all-databases > backup_all_databases.sql
```

# Install Dependencies

## Incubator

```
cd /usr/share/icingaweb2/modules
git clone https://github.com/Icinga/icingaweb2-module-incubator --branch v0.14.0 incubator
chown -R www-data:icingaweb2 incubator
icingacli module enable incubator
```

## React Bundle

```
cd /usr/share/icingaweb2/modules
git clone https://github.com/Icinga/icingaweb2-module-reactbundle --branch v0.9.0 reactbundle
chown -R www-data:icingaweb2 reactbundle
icingacli module enable reactbundle
```

# Install  Upgrade

```
cd /usr/share/icingaweb2/modules
git clone https://github.com/icinga/icingaweb2-module-director director
chown -R www-data:icingaweb2 director
icingacli module enable director
```

# Migrate data

In WebUI go to:
`Configuration -> Modules -> director -> Configuration -> Migrate Data`


## Director Daemon

Create system user `icingadirector`:
```
useradd -r -g icingaweb2 -d /var/lib/icingadirector -s /bin/false icingadirector
install -d -o icingadirector -g icingaweb2 -m 0750 /var/lib/icingadirector
```

Copy system init script and inscribe daemon:
```

```
MODULE_PATH=/usr/share/icingaweb2/modules/director
cp "${MODULE_PATH}/contrib/systemd/icinga-director.service" /etc/systemd/system/
systemctl daemon-reload
```

Enable it:
`systemctl enable icinga-director.service`

Start Director Deamon:
`systemctl start icinga-director.service`



|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
