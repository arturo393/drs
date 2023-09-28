#!/bin/sh

boalog_path="/var/log/boa"
if [ -d $boalog_path ]; then
	rm $boalog_path/*log
fi

cp /tmp/www/daemon_ctrl /usr/bin/
chmod 755 /usr/bin/daemon_ctrl
daemon_ctrl repeater_service "" 0
daemon_ctrl temp "" 0
daemon_ctrl uart_transparent "" 0
killall -9 daemon
cp /tmp/www/daemon /usr/bin
chmod 755 /usr/bin/daemon
killall -9 repeater_service
cp /tmp/www/repeater_service /usr/bin
chmod 755 /usr/bin/repeater_service
killall -9 temp
cp /tmp/www/temp /usr/bin
chmod 755 /usr/bin/temp
killall -9 uart_transparent
cp /tmp/www/uart_transparent /usr/bin
chmod 755 /usr/bin/uart_transparent
cp /tmp/www/init_module /usr/bin/
chmod 755 /usr/bin/init_module
cp /tmp/www/rcS /etc/init.d/
chmod 755 /etc/init.d/rcS
:<<!
cp /tmp/www/libstdc++.so.6.0.19 /lib/
chmod 755 /lib/libstdc++.so.6.0.19
ln -s /lib/libstdc++.so.6.0.19 /lib/libstdc++.so
ln -s /lib/libstdc++.so.6.0.19 /lib/libstdc++.so.6
!
cp /tmp/www/log_cat /usr/bin/
chmod 755 /usr/bin/log_cat
cp /tmp/www/create_db /home/
chmod 755 /home/create_db
cp /tmp/www/Cryptographic /home
cp /tmp/www/upfpga_75t /usr/bin
cp /tmp/www/upfpga_200t /usr/bin
cp /tmp/www/upfpga_bin /usr/bin
chmod 755 /usr/bin/up*
cp /tmp/www/boa_200t /sbin/
chmod 755 /sbin/boa_200t
cp /tmp/www/boa.conf /etc/boa/
chmod 755 /etc/boa/boa.conf
killall -9 auto_topo_ip
cp /tmp/www/auto_topo_ip /usr/bin
chmod 755 /usr/bin/auto_topo_ip
killall -9 sync_rfpoint
cp /tmp/www/sync_rfpoint /usr/bin
chmod 755 /usr/bin/sync_rfpoint
killall -9 delay_sync
cp /tmp/www/delay_sync /usr/bin
chmod 755 /usr/bin/delay_sync
killall -9 led
cp /tmp/www/led /usr/bin
chmod 755 /usr/bin/led

cp /tmp/www/db_copy.sh /home
cp /tmp/www/*.html /var/www
cp -r /tmp/www/layui /var/www 
cp -r /tmp/www/js /var/www
cp -r /tmp/www/cgi-bin /var/www
cp /tmp/www/cgi-bin/update.cgi /var/www/cgi-bin/copy_update.cgi
cp /tmp/www/cgi-bin/module.cgi /var/www/cgi-bin/copy_module.cgi
cp -r /tmp/www/css /var/www
cp -r /tmp/www/images /var/www
cp /tmp/www/favicon.ico /var/www

cp /tmp/www/syspar.ini /home
cp /tmp/www/tempcomp.ini /home
cp /tmp/www/syspar.db /var/www
cp /tmp/www/syspar.db /var/www/same.db
cp /tmp/www/syspar.db /var/www/factory.db
if [ ! -s /var/www/tempcomp.db ]; then 
	cp /tmp/www/tempcomp.db /var/www
fi

chmod 777 /var/www/cgi-bin/*.cgi
cp /tmp/www/web_L-R_shift.sh /home/
cp /tmp/www/update.sh /home/

cp /tmp/www/softversion.txt /var/www

rm -f /tmp/update > /dev/null 2>&1
rm -rf /tmp/www > /dev/null 2>&1


