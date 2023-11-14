<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2
namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;
use Icinga\Module\Rs485\Database;
use ipl\Sql\Select;

class HostForm extends ConfigForm
{
    use Database;

    private $listComando = [

        1, # 'Working mode','Set', '7E', '07','00','00','80','00', '01', '02','0fD7', '7E');
        2, #'Gain power control ATT','Set','7E','07','00','00','E7','00','02','0034','7783','7E');
        3, #'Channel Activation Status','Set','7E','07','00','00','41','00','10','010101011101010101010101010101','11BD','7E');
        4, #'Channel Frequency Point Configuration','Set','7E','07','00','00','35','00','40','B02741002D28410027294100A4294100212A41009E2A41001B2B4100982B4100152C4100922C41000F2D41008C2D4100092E4100862E4100032F4100802F4100','7783','7E');
        5, #'Optical PortState','Set','7E','07','00','00','90','00','04','00010001','9532','7E');


    ];

    public function init()
    {
        $this->setName('form_host');
        $this->setSubmitLabel($this->translate('Submit Changes'));
        $this->setAction('rs485/host/edit');
    }

    public function refresh(string $host, int $centerUplinkFrequency, int $centerDownlinkFrequency, int $bandwidth, string $cmd_type, string $device): void
    {
        $this->setName('form_host');
        $this->setSubmitLabel($this->translate('Submit Changes'));
        $this->setAction(sprintf('rs485/host/edit?host=%s&center_uplink_frequency=%d&center_downlink_frequency=%d&bandwidth=%d&cmd_type=%s&device=%s', $host, $centerUplinkFrequency, $centerDownlinkFrequency, $bandwidth, $cmd_type, $device));
    }

    public function createElements(array $formData)
    {
        $hostname = $_GET['host'] ?? "";
        $listHost = $this->cargarHostList($hostname);
        $listTrama = $this->tramasDMU($hostname);
        $center_uplink_frequency = $_GET['center_uplink_frequency'] ?? 0;
        $center_downlink_frequency = $_GET['center_downlink_frequency'] ?? 0;
        $bandwidth = $_GET['bandwidth'] ?? 0;
        $cmd_type = $_GET['cmd_type'] ?? "";
        $device = $_GET['device'] ?? "";
        $host = $_GET['host'] ?? "";
        $this->refresh($host, $center_uplink_frequency, $center_downlink_frequency, $bandwidth, $cmd_type, $device);

        $this->addElement('select', 'host_remote', array(
            'multiOptions' => $listHost,
            'required' => true,
        ));

        $this->addElement('select', 'trama', array(
            'multiOptions' => $listTrama,
            'value' => '',
            'required' => false,
            'class' => 'autosubmit'
        ));

        if ((isset($formData['trama']) && $formData['trama'] != '') || isset($formData['btn_submit'])) {
            $option = isset($formData['btn_submit']) ? 0 : $formData['trama'];
            #5: Optical PortState
            if ($option == 5 || $option == 999 || isset($formData['opt5_hidden'])) {
                $input = 5;

                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('checkbox', "opt{$input}_1", ['label' => "Enable - Port 1"]);

                    $this->addElement('checkbox', "opt{$input}_2", ['label' => "Enable - Port 2"]);

                    $this->addElement('checkbox', "opt{$input}_3", ['label' => "Enable - Port 3"]);

                    $this->addElement('checkbox', "opt{$input}_4", ['label' => "Enable - Port 4"]);
                }
            }
            #1: Working mode
            if ($option == 1 || $option == 999 || isset($formData["opt1_hidden"])) {
                $input = 1;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('radio', "opt{$input}", array(
                        'label' => $this->translate($descripcion),
                        'multiOptions' => ['03' => 'Channel Mode',
                            '02' => 'WideBand Mode'],
                        'required' => true,
                    ));
                }
            }
            #2: Gain power control ATT
            if ($option == 2 || $option == 999 || isset($formData['opt2_hidden'])) {
                $input = 2;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}_1", ['label' => "Uplink ATT [dB]", 'placeholder' => 'between 0[dB] and 30[dB]', 'required' => true,]);
                    $this->addElement('text', "opt{$input}_2", ['label' => 'Downlink ATT [dB]', 'placeholder' => 'between 0[dB] and 30[dB]', 'required' => true,]);
                }
            }
            #3: Channel Activation Status
            if ($option == 3 || $option == 999 || isset($formData['opt3_hidden'])) {
                $input = 3;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    for ($i = 1; $i <= 16; $i++) {
                        $this->addElement('radio', "opt{$input}_{$i}", array(
                            'label' => $this->translate("Channel {$i}"),
                            'multiOptions' => [1 => 'ON',
                                0 => 'OFF'],
                            'required' => true,

                        ));

                    }
                }
            }
            #4: Channel Frecuency Point Configuration
            if ($option == 4 || $option == 999 || isset($formData['opt4_hidden'])) {
                $input = 4;
                $hidden = $formData["opt{$input}_hidden"] ?? 0;
                if ($option != $hidden) {
                    $listFrecuencia = $this->frequencyTables($center_downlink_frequency, $center_uplink_frequency, $bandwidth);
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    for ($i = 1; $i <= 16; $i++) {
                        $this->addElement('select', "opt{$input}_{$i}", array(
                            'label' => $this->translate("Channel {$i} "),
                            'multiOptions' => $listFrecuencia,
                            'required' => true,
                        ));
                    }
                }
            }
        }
    }

    private function cargarHostList($hostname)
    {
        $select = (new Select())->from('icinga_host r')
            ->columns(['r.*'])
            ->where(['r.object_type = ?' => 'object'])
            ->where("object_name not like '%-opt%'")
            ->orderBy('r.object_name', SORT_ASC);
        $list[''] = '(Master List - IP )';
        foreach ($this->getDb()
                     ->select($select) as $row) {
            $list[$row
                ->id] = "{$row->display_name} - {$row->address}";
            if ($row->object_name == $hostname) {
                $value[$row
                    ->id] = "{$row->display_name} - {$row->address}";
                return $value;
            }
        }
        return $list;
    }

    private function tramasDMU($host)
    {
        $select = (new Select())->from('rs485_dmu_trama r')
            ->columns(['r.*'])
            ->orderBy('r.name', SORT_ASC);
        $list[''] = '(Parameter List)';

        foreach ($this->getDb()
                     ->select($select) as $row) {
            if (!(strripos($host, "dru") !== false && ($row->id == 4 || $row->id == 3))) {
                $list[$row
                    ->id] = $row->name;
            }
        }
        $list[999] = 'Setup All Parameters';
        return $list;
    }

    private function getDescripcion($id)
    {
        $select = (new Select())->from('rs485_dmu_trama r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);

        $row = $this->getDb()
            ->select($select)->fetch();

        return $row->name;
    }

    private function frequencyTables($center_downlink_frequency, $center_uplink_frequency, $bandwidth)
    {
        if ($center_downlink_frequency == 0 or $bandwidth == 0 or $center_uplink_frequency == 0) {
            $list = ["Unknown Frequencies"];
        } else {
            $ul = (float)$center_uplink_frequency - (int)($bandwidth) / 2;
            $dl = (float)$center_downlink_frequency - (int)($bandwidth) / 2;
            $wb = $bandwidth;
            $cb = 125; // 12.5 Khz
            $ch_number_length = 4;

            $total_channel = ($wb / $cb) * 10000;
            for ($i = 0; $i < $total_channel + 1; $i++) {
                $dl_real = $dl * 10000 + $i * $cb;
                $ul_real = $ul * 10000 + $i * $cb;
                $hex = dechex($dl_real);

                $hex_1 = substr($hex, 4, strlen($hex));
                $hex_2 = substr($hex, 2, -2);
                $hex_3 = substr($hex, 0, -4);

                if ($hex_1 == "7f" or $hex_1 == "7e")
                    $hex_1 = "7d";
                if ($hex_2 == "7f" or $hex_2 == "7e")
                    $hex_2 = "7d";
                if ($hex_3 == "7e" or $hex_3 == "7f")
                    $hex_3 = "7d";

                $hex_code = strtoupper($hex_1 . $hex_2 . $hex_3) . "00";

                $channel_number = $i;
                $freq_number_length = 8;

                if (($ul_real) % 10000 == 0) {
                    $ul_real = strval($ul_real / 10000) . ".";
                    $dl_real = strval($dl_real / 10000) . ".";
                } else {
                    $ul_real = strval($ul_real / 10000);
                    $dl_real = strval($dl_real / 10000);
                }
                $ul_real = str_pad($ul_real, $freq_number_length, "0", STR_PAD_RIGHT);
                $dl_real = str_pad($dl_real, $freq_number_length, "0", STR_PAD_RIGHT);

                $ch_number = substr(str_repeat(0, $ch_number_length) . $channel_number, -$ch_number_length);
                if ($hex_code != "")
                    $list[$hex_code] = "CH " . $ch_number . " - UL [MHZ] : " . $ul_real . " - DL [MHZ] : " . $dl_real;
            }
        }
        return $list;
    }
}

