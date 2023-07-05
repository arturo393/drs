| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Master: Graphite Module

## Graphite

### Install Graphite

```
apt install docker docker-compose -y
mkdir -p /opt/docker-compose

echo -n 'version: '2'
services:
  graphite:
    image: graphiteapp/graphite-statsd:latest
    container_name: graphite
    restart: on-failure:5
    hostname: graphite
    volumes:
      - /opt/graphite/conf:/opt/graphite/conf
      - /opt/graphite/storage:/opt/graphite/storage
      - /opt/graphite/log/graphite:/var/log/graphite
      - /opt/graphite/log/carbon:/var/log/carbon
    ports:
      - 2003:2003
      - 8080:80' > /opt/docker-compose/docker-compose.yml

echo -n '[Unit]
Description=docker-compose
Requires=docker.service
After=docker.service

[Service]
Restart=always
User=root
Group=docker
WorkingDirectory=/opt/docker-compose
# Shutdown container (if running) when unit is started
ExecStartPre=/usr/bin/docker-compose -f docker-compose.yml down
# Start container when unit is started
ExecStart=/usr/bin/docker-compose -f docker-compose.yml up
# Stop container when unit is stopped
ExecStop=/usr/bin/docker-compose -f docker-compose.yml down

[Install]
WantedBy=multi-user.target' > /etc/systemd/system/docker-compose.service

systemctl enable docker-compose
systemctl start docker-compose
docker ps -a|grep Up

```

### Change graphite default user/pass = (root/root)

- http://MASTER-host-ip:8080/admin/auth/user/1
- http://MASTER-host-ip:8080/admin/auth/user/1/password/

`systemctl restart docker-composer`

#### References:

- https://computingforgeeks.com/install-graphite-graphite-web-on-centos-rhel/

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

```
cd /usr/share/icingaweb2/modules/
git clone https://github.com/Icinga/icingaweb2-module-graphite graphite
cd graphite
chown -R apache: .
```

# Configure Satellite

Only if icinganweb2 is installed on satellite

## Install Graphite Icingaweb2 Module

Install if you installed Icingaweb2 on Satellite

```
cd /usr/share/icingaweb2/modules/
git clone https://github.com/Icinga/icingaweb2-module-graphite graphite
cd graphite
chown -R www-data:icingaweb2 .
```

Enable módule in Icingaweb2
Configurations->Modules->Graphite->Backend->:

- Graphite Web URL: http://MASTER-host-ip:8080

# Copy Templates
`cp REPO/modules/graphite/templates/default.ini /usr/share/icingaweb2/modules/graphite/templates/`
`cp REPO/modules/graphite/templates/hostalive.ini /usr/share/icingaweb2/modules/graphite/templates/`
# File permissions
ensure file permissions are correct:
`chown -R www-data:icingaweb2 /usr/share/icingaweb2/modules/graphite/templates`

#Copy storage-schemas.conf

`cp REPO/modules/graphite/templates/storage-schemas.confg /opt/graphite/conf`

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
