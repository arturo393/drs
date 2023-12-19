<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2
namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;
use Icinga\Module\Rs485\Database;
use ipl\Sql\Select;

class HostForm extends ConfigForm
{
    use Database;

    public function init()
    {
        $this->setName('form_host');
        $this->setSubmitLabel($this->translate('Submit Changes'));
        $this->setAction('rs485/host/edit');
    }

    public function refresh(string $host, float $centerUplinkFrequency, float $centerDownlinkFrequency, int $bandwidth, string $cmd_type, string $device): void
    {
        $this->setName('form_host');
        $this->setSubmitLabel($this->translate('Submit Changes'));
        $this->setAction(sprintf('rs485/host/edit?host=%s&center_uplink_frequency=%f&center_downlink_frequency=%f&bandwidth=%d&cmd_type=%s&device=%s', $host, $centerUplinkFrequency, $centerDownlinkFrequency, $bandwidth, $cmd_type, $device));
    }

    public function createElements(array $formData)
    {
        $hostname = $_GET['host'] ?? "";
        $listHost = $this->cargarHostList($hostname);
        $center_uplink_frequency = $_GET['center_uplink_frequency'] ?? 0;
        $center_downlink_frequency = $_GET['center_downlink_frequency'] ?? 0;
        $bandwidth = $_GET['bandwidth'] ?? 0;
        $host = $_GET['host'] ?? 0;
        $cmd_type = $_GET['host'] ?? "";
        $device = $_GET['device'] ?? "";

        #$this->refresh($host, $center_uplink_frequency, $center_downlink_frequency, $bandwidth, $cmd_type, $device);


        $this->addElement('select', 'host_remote', array(
            'multiOptions' => $listHost,
            'required' => true,
        ));

        if ($device == 'dmu_ethernet' || $device == 'dru_ethernet' || $device == 'dmu_serial_service') {
            $this->refresh($host, $center_uplink_frequency, $center_downlink_frequency, $bandwidth, $cmd_type, $device);
            $listTrama = $this->tramasDMU($hostname);
        }

        if ($device == 'dru_serial_service') {
            $address = $_GET['address'] ?? "0";
            $baud_rate = $_GET['baudrate'] ?? 0;
            $baud_rate = $_GET['baudrate'] ?? 0;
            $opt_dru_list = $this->decodeAddress($address);
            $opt_dru = 'Optical Port ' . $opt_dru_list[0] . ' Remote ' . $opt_dru_list[1];
            $list[$opt_dru_list[0] . $opt_dru_list[1]] = $opt_dru;
            $listIdDRU = $list;
            //print_r($_GET);
            $this->setName('form_host');
            $this->setSubmitLabel($this->translate('Submit Changes'));
            $this->setAction(sprintf(
                '/rs485/host/edit?host=%s&device=%s&baudrate=%s&address=%s',
                $host, $device, $baud_rate, $address));


            $this->addElement(
                'select',
                'dru_id',
                array(
                    #'label' => $this->translate('Dru Id'),
                    'multiOptions' => $listIdDRU,
                    'required' => true,
                    // 'autosubmit' acts like an AJAX-Request
                    //'class' => 'autosubmit'
                )
            );

            $listTrama = $this->tramasDRUList();
        }

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
                    for ($i = 1; $i <= 16; $i++) {
                        $this->addElement('select', "opt{$input}_{$i}", array(
                            'label' => $this->translate("Channel {$i} "),
                            'multiOptions' => $listFrecuencia,
                            'required' => true,
                        ));
                    }
                }
            }


            #22: Uplink ATT [dB]
            if ($option == 22 || isset($formData["opt22_hidden"])) {
                $input = 22;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $this->addElement('text', "opt{$input}", [
                        'placeholder' => $this->translate("Uplink ATT [dB]") . '       - value between 0[dB] - 40[dB]',
                        'required' => true,
                    ]);
                }
            }
            #23: Downlink ATT [dB]
            if ($option == 23 || isset($formData["opt23_hidden"])) {
                $input = 23;
                $hidden = $formData["opt{$input}_hidden"] ?? 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $this->addElement('text', "opt{$input}", [
                        'placeholder' => $this->translate("Downlink ATT [dB]") . '   - value between 0[dB] - 40[dB]',
                        'required' => true,
                    ]);
                }
            }
            #25: Choice of working mode
            if ($option == 25 || isset($formData["opt25_hidden"])) {
                $input = 25;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $this->addElement(
                        'radio',
                        "opt{$input}",
                        array(
                            'placeholder' => $this->translate("Choice of working mode"),
                            'multiOptions' => [
                                '02' => 'WideBand Mode',
                                '03' => 'Channel Mode'
                            ],
                            'required' => true,
                            // 'autosubmit' acts like an AJAX-Request
                            //'class' => 'autosubmit'
                        )
                    );

                }
            }
            #26: Uplink Start Frequency
            if ($option == 26 || isset($formData['opt26_hidden'])) {
                $input = 26;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {

                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $this->addElement('text', "opt{$input}", [
                        'placeholder' => $this->translate("Uplink Start Frequency") . '   - Insert frequency[MHz]',
                        'required' => true,
                    ]);

                }
            }
            #27: Downlink Start Frequency
            if ($option == 27 || isset($formData['opt27_hidden'])) {
                $input = 27;
                $hidden = $formData["opt{$input}_hidden"] ?? 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $this->addElement('text', "opt{$input}", [
                        'placeholder' => $this->translate("Downlink Start Frequency") . '   - Insert frequency[MHz]',
                        'required' => true,
                    ]);
                }
            }
            #28: Work bandwidth
            if ($option == 28 || isset($formData['opt28_hidden'])) {
                $input = 28;
                $hidden = $formData["opt{$input}_hidden"] ?? 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $this->addElement('text', "opt{$input}", [
                        'placeholder' => $this->translate("Work bandwidth") . '   - Insert frequency[MHz]',
                        'required' => true,
                    ]);
                }
            }
            #29: Channel bandwidth
            if ($option == 29 || isset($formData['opt29_hidden'])) {
                $input = 29;
                $hidden = $formData["opt{$input}_hidden"] ?? 0;
                if ($option != $hidden) {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $this->addElement('text', "opt{$input}", [
                        'placeholder' => $this->translate("Channel bandwidth") . '   - Insert frequency[KHz]',
                        'required' => true,
                    ]);
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
                $list[$row->id] = $row->name;
            }
        }
        $list[999] = 'Setup All Parameters';
        return $list;
    }


    private function tramasDRUList()
    {
        $listComando = [
            # 15, #15: Upstream noise switch
            # 16, #16: High threshold of upstream soise
            # 17, #17: Low threshold of upstream noise
            # 18, #18: Uplink noise correction value
            # 19, #19: Uplink noise Detection parameter 1
            # 20, #20: Uplink noise Detection parameter 2
            22, #22: Uplink ATT [dB]  - Cmd data 0x04004
            23, #23: Downlink ATT [dB] - Cmd data 0x04104
            25, #25: Choice of working mode - Cmd data 0xEF0B
            26, #26: Uplink Start Frequency
            27, #27: Downlink Start Frequency
            28, #28: Work Bandwidth
            29, #29: Channel bandwidth
            #30  #30: Master/Slave Link Alarm Control
            #31: Device Serial Numner
            #32: MAC Address
        ];

        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->where(['r.id  in (?)' => $listComando])
            ->orderBy('r.name', SORT_ASC);

        $list[''] = '(Parameters)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;

        }
        return $list;
    }

    private function listDRU($opt_dru)
    {
        $id = $this->getIdDataList('druIDDataList');
        $select = (new Select())
            ->from('director_datalist_entry r')
            ->columns(['r.*'])
            ->where(['r.list_id  = ?' => $id])
            ->orderBy('r.entry_value', SORT_ASC);

        $list[''] = '(Remotes)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->entry_name] = $row->entry_value;
            if ($row->entry_value == $opt_dru) {
                $value[$row->entry_name] = $row->entry_value;
                return $value;
            }
        }
        return $list;
    }

    private function getIdDataList($nameList)
    {
        $select = (new Select())
            ->from('director_datalist r')
            ->columns(['r.*'])
            ->where(['r.list_name = ?' => $nameList]);
        $row = $this->getDb()->select($select)->fetch();

        return $row->id;
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

    private function decodeAddress(string $address): array
    {
        if (substr($address, 0, 10) !== '192.168.11') {
            return [0, 0];
        }

        if ($address === "192.168.11.22") {
            return [0, 0];
        }

        $opt = 0;

        switch (substr($address, 0, 13)) {
            case "192.168.11.10":
                $opt = 1;
                break;
            case "192.168.11.12":
                $opt = 2;
                break;
            case "192.168.11.14":
                $opt = 3;
                break;
            case "192.168.11.16":
                $opt = 4;
                break;
        }
        $dru = (int)rtrim($address, ")")[-1] + 1; // Use rtrim with ")" to handle potential suffix

        return [$opt, $dru];
    }

    private function frequencyTables($center_downlink_frequency, $center_uplink_frequency, $bandwidth)
    {
        if ($center_downlink_frequency == 0 or $bandwidth == 0 or $center_uplink_frequency == 0) {
            $list = ["Unknown Frequencies"];
        } else {
            $half_bandwidth = ($bandwidth / 2.0);
            $ul = (float)$center_uplink_frequency - ($bandwidth / 2.0);
            $dl = (float)$center_downlink_frequency - ($bandwidth / 2.0);
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

