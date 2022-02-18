<?php

namespace Icinga\Module\Rs485\Controllers;


use Icinga\Web\Controller;


class FileController extends Controller
{
    private $arraySet = array(
       array('id' => 1, 
             'name' => 'Site Number (DMU ID)', 
             'header' => '7E', 
             'x1' => '01 01' ,
             'site_number' => '00 00 00 00',
             'dru_id' => '11' ,
             'x2' => '01 00' ,
             'tx_rx1' => '80' ,
             'x3' => '01' ,
             'message_type' => '03' ,
             'tx_rx2' => 'FF' ,
             'cmd_length' => '07' ,
             'cmd_code' => '01 01' ,
             'cmd_data' => '00 00 00 00' ,
             'crc' => 'DB 30' ,
             'end' => '7E' 
             ) ,

       array('id' => 2, 
             'name' => 'Site Subnumber (DRU ID)', 
             'header' => '7E', 
             'x1' => '00 00', 
             'site_number' => '00 00 00 00',
             'dru_id' => '11' ,
             'x2' => '01 00' ,
             'tx_rx1' => '80' ,
             'x3' => '01' ,
             'message_type' => '03' ,
             'tx_rx2' => 'FF' ,
             'cmd_length' => '04' ,
             'cmd_code' => '02 01' ,
             'cmd_data' => '11' ,
             'crc' => 'B7 E0' ,
             'end' => '7E' 
             )  
        );
    public function init()
    {
        $this->assertPermission('config/modules');
        parent::init();
    }

    public function loadFile($path)
    {
        
        $handle = fopen("rdu-set.csv", "r");
        $lineNumber = 1;
        while (($raw_string = fgets($handle)) !== false) {
            $row = str_getcsv($raw_string);
            var_dump($row);
            $lineNumber++;
        }
        fclose($handle);
    }



    


    
    

    

}

