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
        $this->assertPermission('config/modules');
        parent::init();
    }


    public function editAction()
    {
        $form = (new RemoteForm())
            ->setIniConfig(Config::module('rs485'));

        $btnSubmit = $this->_hasParam('btn_submit') ?  $this->_getParam('btn_submit') : '';
        if($btnSubmit == 'Enviar' ) {
            $error = false;
            $validaRepetidos =  $this->_hasParam('opt4_hidden') ? true : false;     
            if ($validaRepetidos) {
                $errorRepetidos = $this->validaRepetidos();
                if ($errorRepetidos > 0){                    
                    $form->addError("El canal {$errorRepetidos} tiene una frecuencia repetida");
                    $error = true;
                }
            }
            
            $validaRango =   $this->_hasParam('opt2_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt2_1'))) {
                    $desc = $this->getDescripcion($this->_getParam('opt2_hidden'));
                    $form->addError("{$desc} Uplink ATT [dB]: El valor {$this->_getParam('opt2_1')} esta fuera de rango [0 - 40]");
                    $error = true;
                }

                if (!$this->validaRango($this->_getParam('opt2_2'))) {
                    $desc = $this->getDescripcion($this->_getParam('opt2_hidden'));
                    $form->addError("{$desc} Downlink ATT [dB]: El valor {$this->_getParam('opt2_2')} esta fuera de rango [0 - 40]");
                    $error = true;
                }
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


    public function saveAction()
    {
        $result = [];
        $dmuDevice1 = -1;
        $dmuDevice2 = -1;
        $dmuCmdLength = -1;    
        $dmuCmdData = -1;
        $host_remote = $this->buscarIpHost($this->_getParam('host_remote'));
        #1: Working mode 
        if ($this->_hasParam('opt1_hidden')){
            $trama = $this->tramasDMU($this->_getParam('opt1_hidden'));            
		    $dmuDevice1 = $trama->dmu_device1;
		    $dmuDevice2 = $trama->dmu_device2;
            $dmuCmdLength = $trama->cmd_body_lenght; 
            $dmuCmdCode = $trama->cmd_number;
            $dmuCmdData = $this->_getParam('opt1');
            $ejecutar = $this->comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida ]);      
            usleep(100000);
        }
        #2: Gain power control ATT
        if ($this->_hasParam('opt2_hidden')){
            $trama = $this->tramasDMU($this->_getParam('opt2_hidden'));            
		    $dmuDevice1 = $trama->dmu_device1;
		    $dmuDevice2 = $trama->dmu_device2;
            $dmuCmdLength = $trama->cmd_body_lenght; 
            $dmuCmdCode = $trama->cmd_number;
            $byte1 = dechex(4 * (int) $this->_getParam('opt2_1'));
            $byte2 = dechex(4* (int) $this->_getParam('opt2_2'));
            $byte1 = str_pad($byte1, 2, "0", STR_PAD_LEFT); 
            $byte2 = str_pad($byte2, 2, "0", STR_PAD_LEFT); 
            $dmuCmdData = "{$byte1}{$byte2}";
            $ejecutar = $this->comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida ]);      
            usleep(100000);
        }
        #3: Channel Activation Status           
        if ($this->_hasParam('opt3_hidden')){
            $trama = $this->tramasDMU($this->_getParam('opt3_hidden'));            
		    $dmuDevice1 = $trama->dmu_device1;
		    $dmuDevice2 = $trama->dmu_device2;
            $dmuCmdLength = $trama->cmd_body_lenght; 
            $dmuCmdCode = $trama->cmd_number;
            $byte = "";
            for ($i=1; $i<=16; $i++){
                $input = $this->_getParam("opt3_{$i}");
                if ($input == 1){
                    $byte = "{$byte}00";
                }else{
                    $byte = "{$byte}01";
                }                
                
            }
            $dmuCmdData = $byte;
            $ejecutar = $this->comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida ]);      
            usleep(100000);
        }
        #4: Channel Frecuency Point Configuration
        if ($this->_hasParam('opt4_hidden')){
            $trama = $this->tramasDMU($this->_getParam('opt4_hidden'));            
		    $dmuDevice1 = $trama->dmu_device1;
		    $dmuDevice2 = $trama->dmu_device2;
            $dmuCmdLength = $trama->cmd_body_lenght; 
            $dmuCmdCode = $trama->cmd_number;
            $byte = "";
            for ($i=1; $i<=16; $i++){
                $input = $this->_getParam("opt4_{$i}");                
                $byte = "{$byte}{$input}";
            }
            $dmuCmdData = $byte;
            $ejecutar = $this->comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida ]);      
            usleep(100000);
        }
        #5: Optical PortState
        if ($this->_hasParam('opt5_hidden')){
            $trama = $this->tramasDMU($this->_getParam('opt5_hidden'));            
		    $dmuDevice1 = $trama->dmu_device1;
		    $dmuDevice2 = $trama->dmu_device2;
            $dmuCmdLength = $trama->cmd_body_lenght; 
            $dmuCmdCode = $trama->cmd_number;
            $byte = "";
            for ($i=1; $i<=4; $i++){
                $input = $this->_getParam("opt5_{$i}");  
                if ($input == 1){
                    $byte = "{$byte}00";
                } else {
                    $byte = "{$byte}01";
                }           
                    
            }
            $dmuCmdData = $byte;
            $ejecutar = $this->comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida ]);      
            usleep(100000);
        }

        $this->view->assign('salida', $result);
        $this->view->assign('cmd', $ejecutar);	
    }

    private function comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData){
        $paramFijos = '--port /dev/ttyS1 --action set --device dru ';
        $paramVariables = "--dmuDevice1 {$dmuDevice1} --dmuDevice2 {$dmuDevice2} --cmdBodyLenght {$dmuCmdLength} --cmdNumber {$dmuCmdCode} --cmdData {$dmuCmdData}";
        $comando = "/usr/lib/monitoring-plugins/check_rs485.py ";
        $ssh = "sudo -u sigmadev ssh sigmadev@{$host_remote} ";
        $ejecutar =  $ssh . $comando . $paramFijos . $paramVariables;
        return $ejecutar;
    }

    private function armaTrama($data)
    {
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

    private function validaRango($value){
        
        if (!is_numeric($value)) 
            return false;
        
        $intValue = (int) $value;

        if ($intValue < 0 || $intValue >40)
            return false;
        
        return true;
 
    }

    private function getDescripcion($id){
        $select = (new Select())
            ->from('rs485_dmu_trama r')
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

    private function tramasDMU($id){
        $select = (new Select())
            ->from('rs485_dmu_trama r')
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

