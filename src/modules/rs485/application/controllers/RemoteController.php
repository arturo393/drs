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
            #22: Uplink ATT [dB]
            $validaRango =   $this->_hasParam('opt22_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt22'))) {
                    $desc = $this->getDescripcion($this->_getParam('opt22_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt22')} esta fuera de rango [0 - 40]");
                    $error = true;
                }                
            }  
            #23: Downlink ATT [dB]
            $validaRango =   $this->_hasParam('opt23_hidden') ? true : false;   
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt23'))) {
                    $desc = $this->getDescripcion($this->_getParam('opt23_hidden'));
                    $form->addError("{$desc} : El valor {$this->_getParam('opt23')} esta fuera de rango [0 - 40]");
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
        $ejecutar = "";
        $host_remote = $this->buscarIpHost($this->_getParam('host_remote'));
        #22: Uplink ATT [dB] 
        if ($this->_hasParam('opt22_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt22_hidden'));   
            $druId =  $trama->dru_id;        
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex(4 * (int) $this->_getParam('opt22'));
            $druCmdData = str_pad($byte1, 2, "0", STR_PAD_LEFT);            
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }

        #23: Downlink ATT [dB]
        if ($this->_hasParam('opt23_hidden')){
            $trama = $this->tramasDRU($this->_getParam('opt23_hidden'));   
            $druId =  $trama->dru_id;        
		    $druCmdLength = $trama->cmd_length; 
            $druCmdCode = $trama->cmd_code;            
            $byte1 = dechex(4 * (int) $this->_getParam('opt23'));
            $druCmdData = str_pad($byte1, 2, "0", STR_PAD_LEFT);            
            $ejecutar = $this->comando($host_remote, $druId, $druCmdLength, $druCmdCode, $druCmdData);     
            $salida = system($ejecutar . " 2>&1");  
            //$salida = "OK";   
            array_push($result, ['comando' => $trama->name , 'resultado' =>  $salida, 'ssh' => $ejecutar ]);      
            usleep(100000);
        }
        
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

