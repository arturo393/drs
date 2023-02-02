<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2
namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;
use Icinga\Module\Rs485\Database;
use ipl\Sql\Select;

class MasterForm extends ConfigForm
{
    use Database;

    public function init()
    {
        $this->setName('form_master');
        $this->setSubmitLabel($this->translate('Submit Changes'));
        $this->setAction('rs485/master/edit');
    }

    public function refresh($frequency)
    {
        $this->setName('form_master');
        $this->setSubmitLabel($this->translate('Submit Changes'));
        $this->setAction('rs485/master/edit?freq=' . $frequency);

        $frequency = isset($_GET['freq']) ? $_GET['freq'] : "";
    }
    public function createElements(array $formData)
    {
        $hostname = '';
        if (isset($_GET['host'])) $hostname = $_GET['host'];
        $listHost = $this->cargarHostList($hostname);
        $listTrama = $this->tramasDMU();
        $frequency = isset($_GET['freq']) ? $_GET['freq'] : "";
        $this->refresh($frequency);


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

        if ((isset($formData['trama']) && $formData['trama'] != '') || isset($formData['btn_submit']))
        {
            $option = isset($formData['btn_submit']) ? 0 : $formData['trama'];

            #5: Optical PortState
            if ($option == 5 || $option == 999 || isset($formData['opt5_hidden']))
            {
                $input = 5;
                echo "sdss";
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden)
                {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('checkbox', "opt{$input}_1", ['label' => "Enable - Port 1"]);

                    $this->addElement('checkbox', "opt{$input}_2", ['label' => "Enable - Port 2"]);

                    $this->addElement('checkbox', "opt{$input}_3", ['label' => "Enable - Port 3"]);

                    $this->addElement('checkbox', "opt{$input}_4", ['label' => "Enable - Port 4"]);
                }
            }
            #1: Working mode
            if ($option == 1 || $option == 999 || isset($formData["opt1_hidden"]))
            {
                $input = 1;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden)
                {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('radio', "opt{$input}", array(
                        'label' => $this->translate($descripcion) ,
                        'multiOptions' => ['03' => 'Channel Mode',
                        '02' => 'WideBand Mode'],
                        'required' => true,
                    ));

                }
            }
            #2: Gain power control ATT
            if ($option == 2 || $option == 999 || isset($formData['opt2_hidden']))
            {
                $input = 2;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden)
                {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}_1", ['label' => "Uplink ATT [dB]", 'placeholder' => 'between 0[dB] and 30[dB]', 'required' => true, ]);

                    $this->addElement('text', "opt{$input}_2", ['label' => 'Downlink ATT [dB]', 'placeholder' => 'between 0[dB] and 30[dB]', 'required' => true,

                    ]);
                }
            }
            #3: Channel Activation Status
            if ($option == 3 || $option == 999 || isset($formData['opt3_hidden']))
            {
                $input = 3;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden)
                {
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    for ($i = 1;$i <= 16;$i++)
                    {
                        $this->addElement('radio', "opt{$input}_{$i}", array(
                            'label' => $this->translate("Channel {$i}") ,
                            'multiOptions' => [1 => 'ON',
                            0 => 'OFF'],
                            'required' => true,
                            
                        ));
                       
                    }
                }
            }
            #4: Channel Frecuency Point Configuration
            if ($option == 4 || $option == 999 || isset($formData['opt4_hidden']))
            {
                $input = 4;
                $hidden = isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden)
                {
                    $listFrecuencia = $this->frequencyTables($frequency);
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    for ($i = 1;$i <= 16;$i++)
                    {
                        $this->addElement('select', "opt{$input}_{$i}", array(
                            'label' => $this->translate("Channel {$i} ") ,
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
            ->select($select) as $row)
        {
            $list[$row
                ->id] = "{$row->display_name} - {$row->address}";
            if ($row->object_name == $hostname)
            {
                $value[$row
                    ->id] = "{$row->display_name} - {$row->address}";
                return $value;
            }
        }
        return $list;
    }

    private function tramasDMU()
    {
        $select = (new Select())->from('rs485_dmu_trama r')
            ->columns(['r.*'])
        
            ->orderBy('r.name', SORT_ASC);
        $list[''] = '(Parameter List)';

        foreach ($this->getDb()
            ->select($select) as $row)
        {
            $list[$row
                ->id] = $row->name;
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
    private function frequencyTables($id)
    {

        if ($id == "vhf")
        {
            $dl = 145;
            $ul = 170;
            $wb = 15;
        }
        else if ($id == "uhf")
        {
            $dl = 427;
            $ul = 417;
            $wb = 3;
        }
        $cb = 125;

        if ($id != "vhf" and $id != "uhf")
        {
            $list = ["Unknown Frequencies"];
        }

        else
        {
            $total_channel = ($wb / $cb) * 10000;
            for ($i = 0;$i < $total_channel + 1;$i++)
            {
                $dl_real = $dl * 10000 + $i * $cb;
                $ul_real = $ul * 10000 + $i * $cb;
                $hex = dechex($dl_real);
                $hex_code = strtoupper(substr($hex, 4, strlen($hex)) . substr($hex, 2, -2) . substr($hex, 0, -4) . "00");
                $list[$hex_code] = "CH " . $i . " - UL [MHZ] : " . strval($ul_real / 10000) . " - DL [MHZ] : " . strval($dl_real / 10000);
            }
        }

        return $list;
    }

    private function frecuenciaDMU($id)
    {
        if ($id == "uhf")
        {
            $select = (new Select())->from('rs485_frecuencia r')
                ->columns(['r.*'])
                ->orderBy('r.channel', SORT_ASC);

            $list[''] = '(Frequencies List)';
        }
        elseif ($id == "vhf")
        {
            $select = (new Select())->from('rs485_frecuencia_vhf r')
                ->columns(['r.*'])
                ->orderBy('r.channel', SORT_ASC);

            $list[''] = '(Frequencies List)';
        }
        else
        {
            $select = (new Select(" "));

            $list[''] = '(Unknown frequency)';
            return $list;
        }

        foreach ($this->getDb()
            ->select($select) as $row)
        {
            $list[$row
                ->code_hex] = $row->description;
        }
        return $list;
    }
}

