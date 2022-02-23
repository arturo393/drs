CREATE DATABASE rs485;
GRANT SELECT, INSERT, UPDATE, DELETE, DROP, CREATE VIEW, INDEX, EXECUTE ON rs485.* TO admin@localhost IDENTIFIED BY 'Admin.123';


pip3 install serial
pip3 install pyserial
pip3 install Crc16Xmodem


 cd /usr/lib/monitoring-plugins/
chmod a+x check_rs485.py
