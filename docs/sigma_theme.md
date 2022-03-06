# IcingaWeb2 Sigma Theme

## Colors:

Edward
#B1B2B2

Deep Cerulean
#0980AA

Bahama Blue
#046C94

Trinidad
#EC5707

## Copy theme module

```
cp -R icingaweb2-theme-sigma /usr/share/icingaweb2/modules/sigma-theme
chown www-data:icingaweb2 /usr/share/icingaweb2/modules/sigma-theme
```

## Enable Module

Configuration -> Modules -> Sigma-theme -> Enable

## Configure theme

Configuration -> Application -> General:

- Default Theme: sigma-theme
- Users Can't Change Theme: yes

## Patch login footer

`vi /usr/share/icingaweb2/application/views/scripts/authentication/login.phtml`

- Change footer information
- Remove social media links

---

# Index

- [Readme](/readme.md)
- [Master Node](/docs/setup_master_debian.md)
- [Satellite Node](/docs/setup_satellite_debian.md)
