## Instalación de templates

```
cd /tmp
git clone https://gitlab.com/itaum/sigma-rds.git
cd sigma-rds
cp src/modules/graphite/templates/dmu_check_rs485.ini /usr/share/icingaweb2/modules/graphite/templates
cp src/modules/graphite/templates/dru_check_rs485.ini /usr/share/icingaweb2/modules/graphite/templates
cp src/modules/graphite/templates/check_rs485.ini /usr/share/icingaweb2/modules/graphite/templates
```