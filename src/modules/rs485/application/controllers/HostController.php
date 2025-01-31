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
            while (!$error && $i <= 32) {
                $existe = $this->_hasParam("opt{$i}_hidden") ? true : false;
                if ($existe) {
                    $i = 100;
                }
                if ($i == 32) {
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

    private function comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate)
    {
        $paramFijos = "-a {$address} -d {$device} -br {$baud_rate} -ct {$cmd_type} -n ${hostname} -l {$cmd_body_length} -c {$cmd_name} -cd {$cmd_data} -b {$bandwidth}";
        $comando = "/usr/lib/nagios/plugins/check_eth.py ";

        $ejecutar = $comando . $paramFijos;
        #print_r($ejecutar);
        return $ejecutar;
    }

    private function comando_ethernet($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth)
    {
        $paramFijos = "-a {$address} -d {$device}  -ct {$cmd_type} -n ${hostname} -l {$cmd_body_length} -c {$cmd_name} -cd {$cmd_data} -b {$bandwidth}";
        $comando = "/usr/lib/nagios/plugins/check_eth.py ";

        $ejecutar = $comando . $paramFijos;
        #print_r($ejecutar);
        return $ejecutar;
    }

    public function saveAction()
    {
        $device = $this->_getParam('device');
        if ($device == 'dmu_ethernet' || $device == 'dru_ethernet' || $device == 'dmu_serial_service') {
            $query = "";
            $queryArray = [];
            $result = [];
            $dmuDevice1 = -1;
            $dmuDevice2 = -1;
            $cmd_body_length = -1;
            $cmd_data = -1;
            $host_remote = $this->buscarIpHost($this->_getParam('host_remote'));
            $host = $this->buscarDataFromDB($this->_getParam('host_remote'));
            $address = $host->address;
            $hostname = $host->object_name;
            $bandwidth = $this->_getParam('bandwidth');
            $cmd_type = 'single_set';
            $baud_rate = $this->_getParam('baudrate');
            #1: Working mode
            if ($this->_hasParam('opt1_hidden')) {
                $trama = $this->tramasDMU($this->_getParam('opt1_hidden'));
                $cmd_data = $this->_getParam('opt1');
                $cmd_name = 0x80;
                $cmd_body_length = 1;
                $salidaArray = [];
                $ejecutar = $this->comando_ethernet($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth);
                exec($ejecutar . " 2>&1", $salidaArray);
                usleep(50000);
                #print_r($salidaArray);
                $salida = $salidaArray[0] == "OK" ? $salidaArray[0] : "Changes were not applied";
                #print_r($salida);
                if ($salidaArray[0] == "OK") {
                    if ($cmd_data == 2) {
                        $salida = "WideBand";
                    } else if ($cmd_data == 3) {
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
                $cmd_name = 0xe7;
                $cmd_body_length = 2;
                $uplink_att = (int)$this->_getParam('opt2_2');
                $downlink_att = (int)$this->_getParam('opt2_1');
                $byte1 = dechex(4 * (int)$this->_getParam('opt2_2'));
                $byte2 = dechex(4 * (int)$this->_getParam('opt2_1'));
                $byte1 = str_pad($byte1, 2, "0", STR_PAD_LEFT);
                $byte2 = str_pad($byte2, 2, "0", STR_PAD_LEFT);
                if ($device == 'dmu_ethernet') {
                    $cmd_data = "{$byte1}{$byte2}";
                } else {
                    $cmd_data = "{$byte2}{$byte1}";
                }
                //print("{$device} {$cmd_data}");
                $salidaArray = [];
                $ejecutar = $this->comando_ethernet($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth);
                exec($ejecutar . " 2>&1", $salidaArray);
                usleep(50000);

                #print_r($salidaArray);
                $salida = $salidaArray[0] == "OK" ? $salidaArray[0] : "Changes were not applied";
                #print_r($salida);
                if ($salidaArray[0] == "OK") {
                    $salida = "Uplink ATT: {$uplink_att} [dB] \n Downlink ATT: {$downlink_att} [dB]";
                }

                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);
            }
            #3: Channel Activation Status
            if ($this->_hasParam('opt3_hidden')) {
                $trama = $this->tramasDMU($this->_getParam('opt3_hidden'));
                $cmd_name = 0x41;
                $cmd_body_length = 0x10;
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
                $cmd_data = $byte;
                $salidaArray = [];
                $ejecutar = $this->comando_ethernet($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth);
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
                $cmd_name = 0x35;
                $cmd_body_length = 0x40;
                $byte = "";
                $message = "<br>";
                for ($i = 1; $i <= 16; $i++) {
                    $input = $this->_getParam("opt4_{$i}");
                    $byte = "{$byte}{$input}";
                    $inverted_bytes = $this->invert_bytes($input);
                    $decimal_value = $this->hex_to_dec($inverted_bytes) / 1000;
                    $message .= "Channel {$i} : {$decimal_value} [MHz] <br>";
                }
                $cmd_data = $byte;
                $salidaArray = [];
                $ejecutar = $this->comando_ethernet($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth);
                exec($ejecutar . " 2>&1", $salidaArray);
                usleep(50000);
                $salida = $salidaArray[0] == "OK" ? $salidaArray[0] : "Changes were not applied";
                if ($salidaArray[0] == "OK") {
                    $salida = $message;
                }
                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);
            }
            #5: Optical PortState
            if ($this->_hasParam('opt5_hidden')) {
                $trama = $this->tramasDMU($this->_getParam('opt5_hidden'));
                $cmd_name = 0x90;
                $cmd_body_length = 4;
                $byte = "";
                $message = "<br>";
                $status = "";
                $ports = 4;
                for ($i = 1; $i <= $ports; $i++) {
                    $input = $this->_getParam("opt5_{$i}");
                    if ($input == 1) {
                        $byte = "{$byte}00";
                        $status = "ON";
                    } else {
                        $byte = "{$byte}01";
                        $status = "OFF";
                    }
                    $message .= "Optical Port {$i} : {$status} <br>";
                }
                $cmd_data = $byte;
                $salidaArray = [];
                $ejecutar = $this->comando_ethernet($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth);
                exec($ejecutar . " 2>&1", $salidaArray);
                usleep(50000);
                $salida = $salidaArray[0] == "OK" ? $salidaArray[0] : "Changes were not applied";
                if ($salidaArray[0] == "OK") {
                    $salida = $message;
                }
                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $query]);
            }
        }
        if ($device == 'dru_serial_service') {
            $result = [];
            $query = "";
            $ejecutar = "";
            $host_remote = $this->buscarIpHost($this->_getParam('host_remote'));
            $druId = $this->_getParam('dru_id');
            $waitForNewSendTime = 100000;
            $host = $this->buscarDataFromDB($this->_getParam('host_remote'));
            $address = $host->address;
            $hostname = $host->object_name;
            $bandwidth = $this->_getParam('bandwidth');
            $bandwidth = 0;
            $baud_rate = $this->_getParam('baudrate');
            $cmd_type = 'single_set';
            $device = $this->_getParam('device');

            #22: Uplink ATT [dB]
            if ($this->_hasParam('opt22_hidden')) {
                $trama = $this->tramasDRU($this->_getParam('opt22_hidden'));
                $cmd_body_length = '04';
                $cmd_name = '4004';
                $byte1 = dechex((int)$this->_getParam('opt22'));
                $cmd_data = str_pad($byte1, 2, "0", STR_PAD_LEFT);
                $ejecutar = $this->comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate);

                $salidaArray = [];
                exec($ejecutar . " 2>&1", $salidaArray);
                $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied";
                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $ejecutar]);
                usleep($waitForNewSendTime);
            }
            #23: Downlink ATT [dB]
            if ($this->_hasParam('opt23_hidden')) {
                $trama = $this->tramasDRU($this->_getParam('opt23_hidden'));
                $cmd_body_length = '04';
                $cmd_name = '4104';
                $byte1 = dechex((int)$this->_getParam('opt23'));
                $cmd_data = str_pad($byte1, 2, "0", STR_PAD_LEFT);
                $ejecutar = $this->comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate);
                $salidaArray = [];
                exec($ejecutar . " 2>&1", $salidaArray);
                $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied";
                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $ejecutar]);
                usleep($waitForNewSendTime);
            }
            #25: Choice of working mode
            if ($this->_hasParam('opt25_hidden')) {
                $trama = $this->tramasDRU($this->_getParam('opt25_hidden'));
                $cmd_body_length = '04';
                $cmd_name = 'EF0B';
                $cmd_data = $this->_getParam('opt25');
                $ejecutar = $this->comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate);
                $salidaArray = [];
                exec($ejecutar . " 2>&1", $salidaArray);
                $salida = count($salidaArray) > 0 ? $salidaArray[0] : "Changes were not applied";
                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $ejecutar]);
                usleep($waitForNewSendTime);
            }
            #26: Uplink Start Frequency
            if ($this->_hasParam('opt26_hidden')) {
                $trama = $this->tramasDRU($this->_getParam('opt26_hidden'));
                $cmd_body_length = '07';
                $cmd_name = '180A';
                $cmd_data = $this->obtenerhexinvertido(((int)$this->_getParam('opt26')), 10000);
                $ejecutar = $this->comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate);
                $salida = system($ejecutar . " 2>&1");
                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $ejecutar]);
                usleep(100000);
            }
            #27: Downlink Start Frequency
            if ($this->_hasParam('opt27_hidden')) {
                $trama = $this->tramasDRU($this->_getParam('opt27_hidden'));
                $cmd_body_length = '07';
                $cmd_name = '190A';
                $cmd_data = $this->obtenerhexinvertido(((int)$this->_getParam('opt27')), 10000);
                $ejecutar = $this->comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate);
                $salida = system($ejecutar . " 2>&1");
                $result[] = ['comando' => $trama->name, 'resultado' => $salida, 'query' => $ejecutar];
                usleep(100000);
            }
            #28: Work bandwidth
            if ($this->_hasParam('opt28_hidden')) {
                $trama = $this->tramasDRU($this->_getParam('opt28_hidden'));
                $cmd_body_length = '07';
                $cmd_name = '1A0A';
                $cmd_data = $this->obtenerhexinvertido(((int)$this->_getParam('opt28')), 10000);
                $ejecutar = $this->comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate);

                $salida = system($ejecutar . " 2>&1");
                //$salida = "OK";
                $result[] = ['comando' => $trama->name, 'resultado' => $salida, 'query' => $ejecutar];
                usleep(100000);
            }
            #29: Channel bandwidth
            if ($this->_hasParam('opt29_hidden')) {
                $trama = $this->tramasDRU($this->_getParam('opt29_hidden'));
                $cmd_body_length = '07';
                $cmd_name = '1B0A';
                $cmd_data = $this->obtenerhexinvertido(((int)$this->_getParam('opt29')), 1);
                $ejecutar = $this->comando($address, $device, $hostname, $cmd_body_length, $cmd_name, $cmd_data, $cmd_type, $bandwidth, $baud_rate);
                $salida = system($ejecutar . " 2>&1");
                array_push($result, ['comando' => $trama->name, 'resultado' => $salida, 'query' => $ejecutar]);
                usleep(100000);
            }
        }
        $this->view->assign('salida', $result);
        $this->view->assign('cmd', $ejecutar);
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

    private function tramasDRU($id)
    {
        $select = (new Select())
            ->from('rs485_dru_trama r')
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

    private function tramasDRUList()
    {
        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->where(['r.id  in (?)' => $this->listComando])
            ->orderBy('r.name', SORT_ASC);

        $list[''] = '(Parameters)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;

        }
        return $list;
    }

    function invert_bytes($bytes_string)
    {
        $inverted_bytes = "";
        for ($i = strlen($bytes_string) / 2 - 1; $i >= 0; $i--) {
            $inverted_bytes .= substr($bytes_string, $i * 2, 2);
        }

        return $inverted_bytes;
    }

    function hex_to_dec($hex_string)
    {
        $decimal_number = 0;
        for ($i = strlen($hex_string) - 1; $i >= 0; $i--) {
            $decimal_number += hexdec($hex_string[$i]) * (16 ** (strlen($hex_string) - $i - 1));
        }

        return $decimal_number;
    }

    private function obtenerhexinvertido($num_dec, $multiplier): string
    {
        $byte1 = dechex($num_dec * $multiplier);
        $hex_code = str_pad($byte1, 8, "0", STR_PAD_LEFT);
        $bytes_length = ((strlen($hex_code)) - (strlen($hex_code) - 2));
        $druCmdData = strtoupper(substr($hex_code, 6, strlen($hex_code)) . substr($hex_code, 4, $bytes_length) . substr($hex_code, 2, 2) . substr($hex_code, 0, $bytes_length));
        return $druCmdData;
    }
}

