| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Add IP to message


```
cd /etc/icinga2/scripts/
vim mail-service-notification.sh
vim mail-host-notification.sh
```
# add filter to info message

108 if [ "${#SERVICEOUTPUT}" -gt 40 ]; then
109   SERVICEOUTPUT="Alert"
110 fi
111


# add IP to service 
```
140 ## Check whether Icinga Web 2 URL was specified.
141 if [ -n "$ICINGAWEB2URL" ] ; then
142   NOTIFICATION_MESSAGE="$NOTIFICATION_MESSAGE
143
144 $ICINGAWEB2URL/monitoring/host/show?host=$(urlencode "$HOSTNAME")"
145 else
146 IP=$(ip route get 8.8.8.8 | awk -F"src " 'NR==1{split($2,a," ");print a[1]}')
147   NOTIFICATION_MESSAGE="$NOTIFICATION_MESSAGE
148 $IP/monitoring/service/show?host=$(urlencode "$HOSTNAME")&service=$(urlencode "$SERVICENAME")"
149
150 fi
```

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
