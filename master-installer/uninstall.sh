#!/bin/bash

# Purge MySQL packages
apt purge mariadb-common mariadb-server mariadb-client -y

# Purge Icinga2 packages
apt purge icinga2 icinga2-bin icinga2-common icinga2-ido-mysql icingaweb2 icingaweb2-common icingaweb2-module-director icingaweb2-module-ipl icingaweb2-module-monitoring icingacli php-icinga icinga2-doc -y

# Purge PHP packages
apt purge php-common libapache2-mod-php7.4 libapache2-mod-php php7.4-curl php7.4-gd php7.4-intl php7.4-mysql php-imagick php7.4-ldap php7.4-mbstring php7.4-pgsql php7.4-soap php7.4-xml apache2-bin apache2-bin apache2-utils      -y

# Remove Icingaweb2 directories
rm -rf /usr/share/icingaweb2
rm -rf /etc/icinga2