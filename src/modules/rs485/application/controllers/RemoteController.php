<?php

namespace Icinga\Module\Rs485\Controllers;

use GuzzleHttp\Psr7\ServerRequest;
use Icinga\Module\Rs485\Database;
use Icinga\Application\Config;
use Icinga\Module\Rs485\Forms\RemoteForm;
use Icinga\Web\Controller;
use ipl\Html\Html;
use ipl\Sql\Select;
use ipl\Web\Url;
use ipl\Web\Widget\ButtonLink;
use ipl\Web\Widget\Icon;
use ipl\Web\Widget\Link;


class RemoteController extends Controller
{
    use Database;

    public function init()
    {
        //$this->assertPermission('config/modules');
        parent::init();
    }


    public function editAction()
    {
        $form = (new RemoteForm())
            ->setIniConfig(Config::module('rs485'));

        $btnSubmit = $this->_hasParam('btn_submit') ?  $this->_getParam('btn_submit') : '';
        if($btnSubmit == 'Submit Changes' ) {
            $error = false;
            #15: Upstream noise switch
            $validaRango =   $this->_hasParam('opt15_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt15'), 0,255)) {
                    $desc = $this->getDescripcion($this->_getParam('opt15_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt15')} esta fuera de rango [0 - 255]");
                    $error = true;
                }               
            }
            #16: High threshold of upstream soise
            $validaRango =   $this->_hasParam('opt16_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt16'), 0,255)) {
                    $desc = $this->getDescripcion($this->_getParam('opt16_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt16')} esta fuera de rango [0 - 255]");
                    $error = true;
                }               
            }
            #17: Low threshold of upstream noise
            $validaRango =   $this->_hasParam('opt17_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt17'), 0,255)) {
                    $desc = $this->getDescripcion($this->_getParam('opt17_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt17')} esta fuera de rango [0 - 255]");
                    $error = true;
                }               
            }
            #18: Uplink noise correction value
            $validaRango =   $this->_hasParam('opt18_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt18'), 0,255)) {
                    $desc = $this->getDescripcion($this->_getParam('opt18_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt18')} esta fuera de rango [0 - 255]");
                    $error = true;
                }               
            }
            #19: Uplink noise Detection parameter 1
            $validaRango =   $this->_hasParam('opt19_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt19'), 0,255)) {
                    $desc = $this->getDescripcion($this->_getParam('opt19_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt19')} esta fuera de rango [0 - 255]");
                    $error = true;
                }               
            }
            #20: Uplink noise Detection parameter 2
            $validaRango =   $this->_hasParam('opt20_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt20'), 0,255)) {
                    $desc = $this->getDescripcion($this->_getParam('opt20_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt20')} esta fuera de rango [0 - 255]");
                    $error = true;
                }               
            }
            #22: Uplink ATT [dB]
            $validaRango =   $this->_hasParam('opt22_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt22'), 0, 40)) {
                    $desc = $this->getDescripcion($this->_getParam('opt22_hidden'));
                    $form->addError("{$desc} : Value {$this->_getParam('opt22')} out of range [0 - 40]");
                    $error = true;
                }                
            }  
            #23: Downlink ATT [dB]
            $validaRango =   $this->_hasParam('opt23_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt23'), 0, 40)) {
                    $desc = $this->getDescripcion($this->_getParam('opt23_hidden'));
                    $form->addError("{$desc} : Value {$this->_getParam('opt23')} out of range [0 - 40]");
                    $error = true;
                }                
            }
            #26: Uplink Start Frequency ATT [Mhz]
            $validaRango =   $this->_hasParam('opt26_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt26'), 417,420)) {
                    $desc = $this->getDescripcion($this->_getParam('opt26_hidden'));
                    $form->addError("{$desc} : Value {$this->_getParam('opt26')} out of range [427 - 430]");
                    $error = true;
                }                
            }            
            #27: Downlink Start Frequency ATT [Mhz]
            $validaRango =   $this->_hasParam('opt27_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt27'),427,430)) {
                    $desc = $this->getDescripcion($this->_getParam('opt27_hidden'));
                    $form->addError("{$desc} : Value {$this->_getParam('opt27')} out of range [417 - 420]");
                    $error = true;
                }                
            }    
            #28: Work bandwidth [Mhz]
            $validaRango =   $this->_hasParam('opt28_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt28'),1,3)) {
                    $desc = $this->getDescripcion($this->_getParam('opt28_hidden'));
                    $form->addError("{$desc} : Value {$this->_getParam('opt28')} out of range [1 - 3]");
                    $error = true;
                }                
            }    
            #29: Channel bandwidth [Mhz]
            $validaRango =   $this->_hasParam('opt29_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRangoFLoat($this->_getParam('opt29'),12.5,20)) {
                    $desc = $this->getDescripcion($this->_getParam('opt29_hidden'));
                    $form->addError("{$desc} : Value {$this->_getParam('opt29')} out of range [12.5 - 20]");
                    $error = true;
                }                
            }                           
            $i = 1;
            while (!$error && $i<=32){
                $existe = $this->_hasParam("opt{$i}_hidden") ? true : false;
                if ($existe) {
                    $i=100;
                }
                if ($i==32){
                    $form->addError("Select a parameter from the list");
                    $error = true;  
                }   
                $i++;
            }
            
            if (!$error) {                
                $params = $this->getRequest()->getParams();
                $module = 'rs485';
                $controller = 'remote';
                $action = 'save';    
                
                $this->_helper->redirector($action,  $controller, $module , $params);
            }
        }
        $form->handleRequest();
        $this->view->form = $form;
       }


    public function saveAction(){
        $result = [];
        $ejecutar = "";
        $host_remote = $this->buscarIpHost($this->_getParam('host_remote'));
        $druId =  $this->_getParam('dru_id');
        $query = "";
        #15: Upstream noise switch
        if ($this->_hasParam('opt15_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt15_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $hex = dechex($this->_getParam('opt15'));
            $druCmdData = str_pad($hex, 2, "0", STR_PAD_LEFT);           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #16: High threshold of upstream soise
        if ($this->_hasParam('opt16_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt16_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $hex = dechex($this->_getParam('opt16'));
            $druCmdData = str_pad($hex, 2, "0", STR_PAD_LEFT);           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #17: Low threshold of upstream noise
        if ($this->_hasParam('opt17_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt17_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $hex = dechex($this->_getParam('opt17'));
            $druCmdData = str_pad($hex, 2, "0", STR_PAD_LEFT);           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }        
        #18: Uplink noise correction value
        if ($this->_hasParam('opt18_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt18_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $hex = dechex($this->_getParam('opt18'));
            $druCmdData = str_pad($hex, 2, "0", STR_PAD_LEFT);           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #19: Uplink noise Detection parameter 1
        if ($this->_hasParam('opt19_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt19_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $hex = dechex($this->_getParam('opt19'));
            $druCmdData = str_pad($hex, 2, "0", STR_PAD_LEFT);           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);
            $salidaArray = [];
            $salida = system($ejecutar . " 2>&1");  
            $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied"; 
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #20: Uplink noise Detection parameter 2
        if ($this->_hasParam('opt20_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt20_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $hex = dechex($this->_getParam('opt20'));
            $druCmdData = str_pad($hex, 2, "0", STR_PAD_LEFT);           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
 
            $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied"; 
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #22: Uplink ATT [dB] 
        if ($this->_hasParam('opt22_hidden')){

            $trama = $this->tramasDRU($this->_getParam('opt22_hidden'));                    
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex((int) $this->_getParam('opt22'));
            $druCmdData = str_pad($byte1, 2, "0", STR_PAD_LEFT);            
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salidaArray = [];
            exec($ejecutar . " 2>&1", $salidaArray);   
            $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied"; 
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #23: Downlink ATT [dB]
        if ($this->_hasParam('opt23_hidden')){

            $trama = $this->tramasDRU($this->_getParam('opt23_hidden'));                  
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex((int) $this->_getParam('opt23'));
            $druCmdData = str_pad($byte1, 2, "0", STR_PAD_LEFT);          
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData); 
            $salidaArray = [];
            exec($ejecutar . " 2>&1", $salidaArray);   
            $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #25: Choice of working mode
        if ($this->_hasParam('opt25_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt25_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $druCmdData = $this->_getParam('opt25');           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salidaArray = [];
            exec($ejecutar . " 2>&1", $salidaArray);   
            $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied"; 
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #26: Uplinkg Start Frequency
        if ($this->_hasParam('opt26_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt26_hidden'));                   
            $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex((int) $this->_getParam('opt26')*10000);
            $druCmdData = str_pad($byte1, 2, "0", STR_PAD_LEFT);     
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #27: Downlink Start Frequency
        if ($this->_hasParam('opt27_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt27_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex((int) $this->_getParam('opt27')*10000);
            $druCmdData = str_pad($byte1, 2, "0", STR_PAD_LEFT);             
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   

            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #28: Work bandwidth
        if ($this->_hasParam('opt28_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt28_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex((int) $this->_getParam('opt28')*10000);
            $druCmdData = str_pad($byte1, 4, "0", STR_PAD_LEFT);          
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #29: Channel bandwidth
        if ($this->_hasParam('opt29_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt29_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex((int) $this->_getParam('opt29')*100);
            $druCmdData = str_pad($byte1, 5, "0", STR_PAD_LEFT);          
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #30: Master/Slave Link Alarm Control
        if ($this->_hasParam('opt30_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt30_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $druCmdData = $this->_getParam('opt30');           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #31: Device Serial Number
        if ($this->_hasParam('opt31_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt31_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;             
            $druCmdData = $this->_getParam('opt31'); 
            $byte1 = bin2hex($this->_getParam('opt31'));
            $str_len = strlen($byte1)/2;
            $size = 20-$str_len;
            $druCmdData = str_pad($byte1, 20*2, "00");             
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        #32: MAC Address
        if ($this->_hasParam('opt32_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt32_hidden'));                   
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;     
            $druCmdData = bin2hex((int) $this->_getParam('opt32'));           
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
       
       # $ejecutarQuery = $this->comando_dru($host_remote, $druId);
       # exec($ejecutarQuery . " 2>&1", $parameters);
	   #   $index = strpos($parameters[0],'|');
      #	$params = substr($parameters[0],0,$index);
        
       # $this->view->assign('params',$params);

        $this->view->assign('salida', $result);

        	
    }

    private function comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData){
        $paramFijos = '--port /dev/ttyS1 --action set --device dru ';
        $paramVariables = "--druId {$druId} --cmdBodyLenght {$druCmdLength} --cmdNumber {$druCmdCode} --cmdData {$druCmdData}";
        $comando = "/usr/lib/monitoring-plugins/check_rs485.py ";
        $ssh = "sudo -u sigmadev ssh sigmadev@{$host_remote} ";
        $ejecutar =  $ssh . $comando . $paramFijos . $paramVariables;
        return $ejecutar;
    }
    
    private function comando_dru($host_remote, $druId){
        $paramFijos = "-o {$druId[0]} -d {$druId[1]}";
        $comando = "/usr/lib/monitoring-plugins/dru_check_rs485.py ";
        $ssh = "sudo -u sigmadev ssh sigmadev@{$host_remote} ";
        $ejecutar =  $ssh . $comando . $paramFijos;
        return $ejecutar;
    }

    private function armaTrama($data){
	   $trama = $data->header . $data->dmu_device1 . $data->dmu_device2 . $data->data_type . $data->cmd_number . $data->response_flag . $data->cmd_body_lenght . $data->cmd_data . $data->crc . $data->end;
	   return $trama; 
    }

    private function validaRepetidos(){
        $exits = 0;
        
        $list = []; 
        for ($i=1; $i<=16 && $exits==0; $i++) {
            $input = $this->_hasParam("opt4_{$i}") ? $this->_getParam("opt4_{$i}") : '';
            if ($input != '') {
                if (in_array($input, $list)){
                    $exits = $i;
                }else{
                    array_push($list, $input);
                }               
            } 
        }
        return $exits;   
    }

    private function validaRango($value, $min, $max){
        
        if (!is_numeric($value)) 
            return false;
        
        $intValue = (int) $value;

        if ($intValue < $min || $intValue > $max)
            return false;
        
        return true;
 
    }

    private function validaRangoFLoat($value, $min, $max){
        
        if (!is_numeric($value)) 
            return false;
        
        $intValue = (float) $value;

        if ($intValue < $min || $intValue > $max)
            return false;
        
        return true;
 
    }

    private function getDescripcion($id){
        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);
      
         $row  = $this->getDb()->select($select)->fetch();

        return $row->name;
    }

    private function frecuenciaDMU($id){
        $select = (new Select())
            ->from('rs485_frecuencia r')
            ->columns(['r.*'])
            ->where(['r.code_hex = ?' => $id]);

        $row  = $this->getDb()->select($select)->fetch();
        return $row;
    }

    private function tramasDRU($id){
        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);
           
        $row  = $this->getDb()->select($select)->fetch();
        return $row;
    }

    private function buscarIpHost($id){
        $select = (new Select())
        ->from('icinga_host r')
        ->columns(['r.*'])
        ->where(['r.id = ?' => $id]);
        $row  = $this->getDb()->select($select)->fetch();
        return $row->address;
}

}

