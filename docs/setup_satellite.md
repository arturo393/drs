# Prerequisites

On master get provisioning ticket:

```
icinga2 pki ticket --cn 'Satellite-FQDN
```

Add new Satellite zone and enpoint:

```
Director->Zone->New Zone {name: "satellite FQDN", Parent Zone: "master"}
Director->Endpoint->New {name: "satellite FQDN", Cluster Zone: "satellite FQDN"}
```

Restart icinga2
`systemctl restart icinga2`

# Install software

```
apt update && apt upgrade
apt install icinga2 monitoring-plugins
```

## Configure node

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

```
