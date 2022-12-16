| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# RS485 Write WebUI Module

console

```
apt install icingaweb2-module-ipl
mysql -p -u root director < /tmp/sigma-rds/src/modules/rs485/schema/mysql.sql
cp -R /tmp/sigma-rds/src/modules/rs485 /usr/share/icingaweb2/modules
chown -R apache:icingaweb2 /usr/share/icingaweb2/modules
```

Enable module http://master-host_ip/icingaweb2/config/modules

## WebUI Setup

### create new DB resource

Configuration -> Applications -> Resources -> Create a New Resource

- Resource Name: `rs485_db`

## Set datasource

Configuration -> Modules -> rs485 -> Backend


# Configure remote execution

To allow master node `RS485 write module` to execute commands on satellite node, you need to configure remote execution.
- [Remote Execution](/docs/remote_execution.md)

# Add or remove entries in the form

edit rs485>>application>>forms>>RemoteForm.php

    use Database;
    private $listComando = [
        # 15, #15: Upstream noise switch
        # 16, #16: High threshold of upstream soise
        # 17, #17: Low threshold of upstream noise
        # 18, #18: Uplink noise correction value
        # 19, #19: Uplink noise Detection parameter 1
        # 20, #20: Uplink noise Detection parameter 2
        22, #22: Uplink ATT [dB]  - Cmd data 0x04004
        23, #23: Downlink ATT [dB] - Cmd data 0x04104
        25, #25: Choice of working mode - Cmd data 0xEF0B
        #  26, #26: Uplinkg Start Frequency
        #  27, #27: Downlink Start Frequency
        #  30  #30: Master/Slave Link Alarm Control
    ];

check avaliable list in rs485>>schema>>mysql.sql

    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Site Number (DMU ID)','Set','7E','0101','00000000','11','0100','80','01','03','FF','07','0101','00000000','DB30','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Site Subnumber (DRU ID)','Set','7E','0101','00000000','11','0100','80','01','03','FF','04','0201','11','B7E0','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Supply power fail alarm','Set','7E','0101','00000000','12','0100','80','01','03','FF','08','0103','0004010200','386','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('PA temphihg alarm','Query','7E','0101','00000000','12','0100','80','01','03','FF','08','0603','0004060200','D71A','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Optical moule TxRx Alarm','Set','7E','0101','00000000','12','0100','80','01','03','FF','08','0E03','00040E0200','DB20','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Master SlaveLink Alarm','Set','7E','0101','00000000','12','0100','80','01','03','FF','08','0F03','00040F0200','8AAF','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('DownLink OverOutput Alarm','Set','7E','0101','00000000','12','0100','80','01','03','FF','08','1203','0004120200','C973','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Downlink LowOutput Alarm','Set','7E','0101','00000000','12','0100','80','01','03','FF','08','1303','0004130200','98FC','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('DownLink VSWR Alarm','Set','7E','0101','00000000','12','0100','80','01','03','FF','08','1403','0004140200','4C60','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Downlinl VSWR Threshold','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','5004','00','A33C','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('PaTemp Threshold','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','5104','00','930B','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('DownLink OutputMin Threshold','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','5504','00','53D7','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('DownLink OutputMax Threshold','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','5604','00','38E','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Alarm Delay','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','270A','00','3442','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Upstream noise switch','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','E00B','00','62D2','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('High threshold of upstream soise','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','E10B','00','52E5','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Low threshold of upstream noise','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','E20B','00','2BC','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Uplink noise correction value','Set','7E','0101','00000000','12','0100','80','01','02','FF','04','E30B','00','328B','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Uplink noise Detection parameter 1','Set','7E','0101','00000000','12','0100','80','01','02','FF','04','E40B','00','A20E','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Uplink noise Detection parameter 2','Set','7E','0101','00000000','12','0100','80','01','02','FF','04','E50B','00','2B9F','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('RF power switch','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','0104','01','8AAC','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Uplink ATT [dB]','Set','7E','0101','00000000','12','0100','80','01','03','FF','04','4004','0000','0000','7F');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Downlink ATT [dB]','Set','7E','0101','55555555','12','0100','80','01','03','FF','04','4104','00','F048','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Channel switch','Set','7E','0101','55555555','12','0100','80','01','03','FF','05','160A','0000','8AAC','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Choice of working mode','Set','7E','0101','55555555','12','0100','80','01','03','FF','04','EF0B','00','53FE','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Uplink Start Frequency [MHz]','Set','7E','0101','00000000','11','0100','80','01','03','FF','07','180A','10A13F00','2452','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Downlink Start Frequency [MHz]','Set','7E','0101','00000000','11','0100','80','01','03','FF','07','190A','B0274100','8417','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Work Bandwidth [MHz]','Set','7E','0101','00000000','11','0100','80','01','03','FF','07','1A0A','30750000','64D9','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Channel bandwidth [KHz]','Set','7E','0101','00000000','11','0100','80','01','03','FF','07','1B0A','7D000000','C49C','7E');
    INSERT INTO rs485_dru_trama (name, type,header, x1, site_number,dru_id,x2,tx_rx1,x3,message_type,tx_rx2,cmd_length,cmd_code, cmd_data,crc,end) VALUES ('Master/Slave Link Alarm Control','Set','7E','0101','00000000','11','0100','80','01','03','FF','04','0F02','00','C49C','7E');



|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
