<?php

namespace Icinga\Module\Rs485\Controllers;

use GuzzleHttp\Psr7\ServerRequest;
use Icinga\Module\Rs485\Database;
use Icinga\Application\Config;
use Icinga\Module\Rs485\Forms\HostForm;
use Icinga\Web\Controller;
use ipl\Html\Html;
use ipl\Sql\Select;
use ipl\Web\Url;
use ipl\Web\Widget\ButtonLink;
use ipl\Web\Widget\Icon;
use ipl\Web\Widget\Link;


class HostController extends Controller
{
    use Database;

    public function init()
    {
        //$this->assertPermission('config/modules');
        parent::init();
    }


    public function editAction()
    {
        $form = (new HostForm())
            ->setIniConfig(Config::module('rs485'));

        $btnSubmit = $this->_hasParam('btn_submit') ? $this->_getParam('btn_submit') : '';
        if ($btnSubmit == 'Submit Changes') {
            $error = false;
            $validaRepetidos = $this->_hasParam('opt4_hidden') ? true : false;
            if ($validaRepetidos) {
                $errorRepetidos = $this->validaRepetidos();
                if ($errorRepetidos > 0) {
                    $form->addError("Channel {$errorRepetidos} is repeated");
                    $error = true;
                }
            }

            $validaRango = $this->_hasParam('opt2_hidden') ? true : false;
            if ($validaRango) {
                if (!$this->validaRango($this->_getParam('opt2_1'))) {
                    $desc = $this->getDescripcion($this->_getParam('opt2_hidden'));
                    $form->addError("{$desc} Uplink ATT [dB]: Value {$this->_getParam('opt2_1')} out of range [0 - 30]");
                    $error = true;
                }

                if (!$this->validaRango($this->_getParam('opt2_2'))) {
                    $desc = $this->getDescripcion($this->_getParam('opt2_hidden'));
                    $form->addError("{$desc} Downlink ATT [dB]: Value {$this->_getParam('opt2_2')} out of range [0 - 40]");
                    $error = true;
                }
            }

            $i = 1;
            while (!$error && $i <= 5) {
                $existe = $this->_hasParam("opt{$i}_hidden") ? true : false;
                if ($existe) {
                    $i = 100;
                }
                if ($i == 5) {
                    $form->addError("Select a parameter");
                    $error = true;
                }
                $i++;
            }

            if (!$error) {
                $params = $this->getRequest()->getParams();
                $module = 'rs485';
                $controller = 'host';
                $action = 'save';

                $this->_helper->redirector($action, $controller, $module, $params);
            }

        }

        $form->handleRequest();

        $this->view->form = $form;


    }


    public function saveAction()
    {
        $query = "";
        $queryArray = [];
        $result = [];
        $dmuDevice1 = -1;
        $dmuDevice2 = -1;
        $dmuCmdLength = -1;
        $dmuCmdData = -1;
        $host_remote = $this->buscarIpHost($this->_getParam('host_remote'));
        $host = $this->buscarDataFromDB($this->_getParam('host_remote'));

        $device_address = $host->address;
        $device_hostname = $host->object_name;
        $device = "dmu";

        #1: Working mode
        if ($this->_hasParam('opt1_hidden')) {
            $trama = $this->tramasDMU($this->_getParam('opt1_hidden'));
            $dmuCmdData = $this->_getParam('opt1');
            $dmuCmdCode = 0x80;
            $dmuCmdLength = 1;
            $salidaArray = [];
            $ejecutar = $this->comando($device_address, $device, $device_hostname, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);
            exec($ejecutar . " 2>&1", $salidaArray);
            usleep(50000);
            $salida = $salidaArray[0] == "OK" ? $salidaArray[0] : "Changes were not applied";
            if ($salidaArray[0] == "OK") {
                if ($dmuCmdData == 2) {
                    $salida = "WideBand";
                } else if ($dmuCmdData == 3) {
                    $salida = "Channel mode";
                } else {
                    $salida = "Unkonw mode";
                }
            }
            array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);

        }
        #2: Gain power control ATT
        if ($this->_hasParam('opt2_hidden')) {
            $trama = $this->tramasDMU($this->_getParam('opt2_hidden'));
            $dmuCmdCode = 0xe7;
            $dmuCmdLength = 2;
            $uplink_att = (int)$this->_getParam('opt2_2');
            $downlink_att = (int)$this->_getParam('opt2_1');
            $byte1 = dechex(4 * (int)$this->_getParam('opt2_2'));
            $byte2 = dechex(4 * (int)$this->_getParam('opt2_1'));
            $byte1 = str_pad($byte1, 2, "0", STR_PAD_LEFT);
            $byte2 = str_pad($byte2, 2, "0", STR_PAD_LEFT);
            $dmuCmdData = "{$byte1}{$byte2}";
            $salidaArray = [];
            $ejecutar = $this->comando($device_address, $device, $device_hostname, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);
            exec($ejecutar . " 2>&1", $salidaArray);
            usleep(50000);
            $salida = $salidaArray[0] == "OK" ? $salidaArray[0] : "Changes were not applied";
            if ($salidaArray[0] == "OK") {
                $salida = "Uplink ATT: {$uplink_att} [dB] \n Downlink ATT: {$downlink_att} [dB]";
            }
            array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);
        }
        #3: Channel Activation Status           
        if ($this->_hasParam('opt3_hidden')) {
            $trama = $this->tramasDMU($this->_getParam('opt3_hidden'));
            $dmuCmdCode = 0x41;
            $dmuCmdLength = 10;
            $byte = "";
            $message = "<br>";
            $status = "";
            for ($i = 1; $i <= 16; $i++) {
                $input = $this->_getParam("opt3_{$i}");
                if ($input == 1) {
                    $byte = "{$byte}00";
                    $status = "ON";
                } else {
                    $byte = "{$byte}01";
                    $status = "OFF";
                }
                $message .= "Channel {$i} : {$status} <br>";
            }
            $dmuCmdData = $byte;
            $salidaArray = [];
            $ejecutar = $this->comando($device_address, $device, $device_hostname, $dmuCmdLength, $dmuCmdCode, $dmuCmdData);
            exec($ejecutar . " 2>&1", $salidaArray);
            usleep(50000);
            $salida = $salidaArray[0] == "OK" ? $salidaArray[0] : "Changes were not applied";
            if ($salidaArray[0] == "OK") {
                $salida = $message;
            }
            array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);

        }
        #4: Channel Frecuency Point Configuration
        if ($this->_hasParam('opt4_hidden')) {
            $trama = $this->tramasDMU($this->_getParam('opt4_hidden'));
            $dmuDevice1 = $trama->dmu_device1;
            $dmuDevice2 = $trama->dmu_device2;
            $dmuCmdLength = $trama->cmd_body_lenght;
            $dmuCmdCode = $trama->cmd_number;
            $byte = "";
            for ($i = 1; $i <= 16; $i++) {
                $input = $this->_getParam("opt4_{$i}");
                $byte = "{$byte}{$input}";
            }
            $dmuCmdData = $byte;
            $salidaArray = [];
            $ejecutar = $this->comando($host_remote, $dmuDevice1, $dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData, 'set');
            exec($ejecutar . " 2>&1", $salidaArray);
            usleep(100000);
            $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied";
            //$salida = "OK";   
            # $queryArray = [];
            # $ejecutarQuery = $this->comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, '36', $dmuCmdData, 'query');
            # exec($ejecutarQuery . " 2>&1", $queryArray);
            # usleep(100000);
            # $query =  count($queryArray) > 0 ? $queryArray[0] : "Changes were not applied";

            array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);
            system("clear  2>&1");
        }
        #5: Optical PortState
        if ($this->_hasParam('opt5_hidden')) {

            $trama = $this->tramasDMU($this->_getParam('opt5_hidden'));
            $dmuDevice1 = $trama->dmu_device1;
            $dmuDevice2 = $trama->dmu_device2;
            $dmuCmdLength = $trama->cmd_body_lenght;
            $dmuCmdCode = $trama->cmd_number;
            $byte = "";
            for ($i = 1; $i <= 4; $i++) {
                $input = $this->_getParam("opt5_{$i}");
                if ($input == 1) {
                    $byte = "{$byte}00";
                } else {
                    $byte = "{$byte}01";
                }

            }
            $dmuCmdData = $byte;
            $salidaArray = [];
            $ejecutar = $this->comando($host_remote, $dmuDevice1, $dmuDevice2, $dmuCmdLength, $dmuCmdCode, $dmuCmdData, 'set');
            exec($ejecutar . " 2>&1", $salidaArray);
            usleep(100000);
            $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied";
            //$salida = "OK";   
            # $queryArray = [];
            # $ejecutarQuery = $this->comando($host_remote, $dmuDevice1,$dmuDevice2, $dmuCmdLength, '91', $dmuCmdData, 'query');
            # exec($ejecutarQuery . " 2>&1", $queryArray);
            # usleep(100000);
            $query = count($queryArray) > 0 ? $queryArray[0] : "Changes were not applied";

            array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);

        }

        #  $ejecutarQuery = $this->comando_dmu($host_remote);
        #  exec($ejecutarQuery . " 2>&1", $parameters);
        #    $index = strpos($parameters[0],'|');
        #	$params = substr($parameters[0],0,$index);

        $this->view->assign('salida', $result);
        $this->view->assign('cmd', $ejecutar);
        #  $this->view->assign('params', $params);
    }

    private function comando($device_address, $device, $hostname, $dmuCmdLength, $dmuCmdCode, $dmuCmdData)
    {
        $paramFijos = "-a {$device_address} -d {$device} -t 1 -n ${hostname} -l {$dmuCmdLength} -c {$dmuCmdCode} -cd {$dmuCmdData} -b 10";
        $comando = "/usr/lib/nagios/plugins/check_status.py ";
        $ejecutar = $comando . $paramFijos;
        echo $ejecutar;
        return $ejecutar;
    }

    private function validaRepetidos()
    {
        $exits = 0;

        $list = [];
        for ($i = 1; $i <= 16 && $exits == 0; $i++) {
            $input = $this->_hasParam("opt4_{$i}") ? $this->_getParam("opt4_{$i}") : '';
            if ($input != '') {
                if (in_array($input, $list)) {
                    $exits = $i;
                } else {
                    array_push($list, $input);
                }
            }
        }
        return $exits;
    }

    private function validaRango($value)
    {

        if (!is_numeric($value))
            return false;

        $intValue = (int)$value;

        if ($intValue < 0 || $intValue > 40)
            return false;

        return true;

    }

    private function getDescripcion($id)
    {
        $select = (new Select())
            ->from('rs485_dmu_trama r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);

        $row = $this->getDb()->select($select)->fetch();

        return $row->name;
    }

    private function tramasDMU($id)
    {
        $select = (new Select())
            ->from('rs485_dmu_trama r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);

        $row = $this->getDb()->select($select)->fetch();
        return $row;
    }

    private function buscarDataFromDB($id)
    {
        $select = (new Select())
            ->from('icinga_host r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);
        $row = $this->getDb()->select($select)->fetch();
        return $row;
    }

    private function buscarIpHost($id)
    {
        $select = (new Select())
            ->from('icinga_host r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);
        $row = $this->getDb()->select($select)->fetch();
        return $row->address;
    }

}

