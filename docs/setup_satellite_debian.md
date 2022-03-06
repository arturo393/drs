# Satellite Node

## Prerequisites

On MASTER node get provisioning ticket:

```
icinga2 pki ticket --cn 'Satellite-FQDN'
```

On MASTER node WebUI add new Satellite zone and enpoint:

```
Director->Zone->New Zone {name: "satellite FQDN", Parent Zone: "master"}
Director->Endpoint->New {name: "satellite FQDN", Cluster Zone: "satellite FQDN"}
```

Restart icinga2
`systemctl restart icinga2`

## Install Satellite software

```
apt update && apt upgrade
apt install icinga2 monitoring-plugins
```

### Configure node

```
icinga2 node wizard


cat << EOF | sudo tee /etc/icinga2/conf.d/api-users.conf
object ApiUser "root" {
  password = "Admin.123"
  permissions = [ "*" ]
}
EOF

echo -n | sudo tee /etc/icinga2/conf.d/{apt.conf,commands.conf,groups.conf,hosts.conf,downtimes.conf,notifications.conf,satellite.conf,services.conf,templates.conf,timeperiods.conf,users.conf}

systemctl restart icinga2

usermod -a -G dialout nagios

```

## Configure Extra Dependencies

- [MOXA Driver](/docs/moxa_drivers.md)
- [Remote Execution](/docs/remote_execution.md)
- [RS485 Plugin](/docs/rs485_plugin.md)
- [WebUI (Optional)](/docs/setup_webui_debian.md)

## Important!

_Do not add Director module to satellite node_

---

# Index

- [Readme](/readme.md)
- [Master Node](/docs/setup_master_debian.md)
- [Satellite Node](/docs/setup_satellite_debian.md)
