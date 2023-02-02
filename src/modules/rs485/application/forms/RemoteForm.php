<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;
use Icinga\Module\Rs485\Database;
use ipl\Sql\Select;

class RemoteForm extends ConfigForm
{
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
         #26: Uplinkg Start Frequency
         #27: Downlink Start Frequency
         #28: Work Bandwidth
         #29: Channel bandwidth
        #30  #30: Master/Slave Link Alarm Control
         #31: Device Serial Numner
         #32: MAC Address
    ];

    public function init()
    {
        $this->setName('form_remote');
        $this->setSubmitLabel($this->translate('Submit Changes'));
        $this->setAction('rs485/remote/edit');
    }

    public function createElements(array $formData)
    {
        $hostname = '';
        $opt_dru = '';
        if (isset($_GET['service'])){
            $servicename = $_GET['service'];
            $hostname = substr($servicename,0, -10);
            #echo json_encode($_GET);
            $opt = substr($servicename,15,-5);
            $dru = substr($servicename,20,);
            $opt_dru = "OPT".$opt." Remote ".$dru;
        }
        $listHost = $this->cargarHostList($hostname);
        $listIdDRU = $this->listDRU($opt_dru);
        $listTrama = $this->tramasDRUList();

        #$this->addDecorator('HtmlTag', array('tag' => 'fieldset', 'openOnly' => true));

        $this->addElement(
            'select',
            'host_remote',
            array(
                #'label' => $this->translate('Host'),
                'multiOptions' => $listHost,
                'required' => true,
                // 'autosubmit' acts like an AJAX-Request
                //'class' => 'autosubmit'
            )
        );

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

        $this->addElement(
            'select',
            'trama',
            array(
                #'label' => $this->translate('Comando'),
                'multiOptions' => $listTrama,
                'value' => '',
                'required' => false,
                // 'autosubmit' acts like an AJAX-Request
                'class' => 'autosubmit'
            )
        );

        if ((isset($formData['trama']) && $formData['trama'] != '') || isset($formData['btn_submit']))  {

            $option = isset($formData['btn_submit']) ? 0 : $formData['trama'];

            #15: Upstream noise switch
            if ($option == 15 ||  isset($formData["opt15_hidden"])) {
                $input = 15;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 255',
                        'required' => true,
                    ]);                     
                }    
            }
            #16: High threshold of upstream soise
            if ($option == 16 ||  isset($formData["opt16_hidden"])) {
                $input = 16;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 255',
                        'required' => true,
                    ]);                     
                }    
            }
            #17: Low threshold of upstream noise
            if ($option == 17 ||  isset($formData["opt17_hidden"])) {
                $input = 17;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 255',
                        'required' => true,
                    ]);                     
                }    
            }
            #18: Uplink noise correction value
            if ($option == 18 ||  isset($formData["opt18_hidden"])) {
                $input = 18;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 255',
                        'required' => true,
                    ]);                     
                }    
            }  
            #19: Uplink noise Detection parameter 1
            if ($option == 19 ||  isset($formData["opt19_hidden"])) {
                $input = 19;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 255',
                        'required' => true,
                    ]);                     
                }    
            }
            #20: Uplink noise Detection parameter 2
            if ($option == 20 ||  isset($formData["opt20_hidden"])) {
                $input = 20;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 255',
                        'required' => true,
                    ]);                     
                }    
            }
            #22: Uplink ATT [dB]
            if ($option == 22 ||  isset($formData["opt22_hidden"])) {
                $input = 22;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        #'label'       => $this->translate("{$descripcion}"),
                        'placeholder' =>$this->translate("{$descripcion}"). '       - value between 0[dB] - 40[dB]',
                        'required' => true,
                    ]);                     
                }    
            } 
            #23: Downlink ATT [dB]
            if ($option == 23 ||  isset($formData["opt23_hidden"])) {
                $input = 23;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        #'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => $this->translate("{$descripcion}").'   - value between 0[dB] - 40[dB]',
                        'required' => true,
                    ]);                     
                }    
            }
            #25: Choice of working mode
            if ($option == 25 ||  isset($formData["opt25_hidden"])) {
                $input = 25;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement(
                        'radio',
                        "opt{$input}",
                        array(
                            'label' => $this->translate($descripcion),
                            'multiOptions' =>[
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
            #26: Uplinkg Start Frequency
            if ($option == 26 ||  isset($formData['opt26_hidden'])) {
                $input = 26;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {      
                    $listFrecuencia = $this->frecuenciaDMU();         
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);                                    
                    $this->addElement('text', "opt{$input}", [
                        #'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => $this->translate("{$descripcion}").'   - value between 417[MHz] - 420[MHz]',
                        'required' => true,
                    ]);  

                }
            }
            #27: Downlink Start Frequency
            if ($option == 27 ||  isset($formData['opt27_hidden'])) {
                $input = 27;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {      
      
                $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                $descripcion = $this->getDescripcion($input);                                    
                $this->addElement('text', "opt{$input}", [
                    #'label'       => $this->translate("{$descripcion}"),
                    'placeholder' => $this->translate("{$descripcion}").'   - value between 427[MHz] - 430[MHz]',
                    'required' => true,
                ]);                      
                }
            }
            #28: Work bandwidth
            if ($option == 28 ||  isset($formData['opt28_hidden'])) {
                $input = 28;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {      
                #    $listFrecuencia = $this->frecuenciaDMU();         
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);                                    
                    $this->addElement('text', "opt{$input}", [
                        #'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => $this->translate("{$descripcion}").'   - value between 1[MHz] - 3[MHz]',
                        'required' => true,
                    ]);  
                }
            }

            #29: Channel bandwidth
            if ($option == 29 ||  isset($formData['opt29_hidden'])) {
                $input = 29;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {            
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);                                    
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);                                    
                    $this->addElement('text', "opt{$input}", [
                        #'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => $this->translate("{$descripcion}").'   - value between 12.5[KHz] - 20[KHz]',
                        'required' => true,
                    ]);                    
                }
            }

            #30: Master/Slave Link Alarm Control
            if ($option == 30 ||  isset($formData["opt30_hidden"])) {
                $input = 30;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement(
                        'radio',
                        "opt{$input}",
                        array(
                            'label' => $this->translate($descripcion),
                            'multiOptions' =>[
                                '01' => 'Enable',
                                '00' => 'Disable'
                            ],
                            'required' => true,
                            // 'autosubmit' acts like an AJAX-Request
                            //'class' => 'autosubmit'
                        )
                    );

                }    
            }                  
            #31: Device Serial number
            if ($option == 31 ||  isset($formData["opt31_hidden"])) {
                $input = 31;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        #'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => $this->translate("{$descripcion}").'   - enter text here',
                        'required' => true,
                    ]);  

                }    
            }
            #32: MAC Address
            if ($option == 32 ||  isset($formData["opt32_hidden"])) {
                $input = 32;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {                                        
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}", [
                        #'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => $this->translate("{$descripcion}").'   - 00-00-00-00-00-00',
                        'required' => true,
                    ]);  

                }    
            }

        }       
    }

    private function cargarHostList($hostname){
        $select = (new Select())
            ->from('icinga_host r')
            ->columns(['r.*'])
            ->where(['r.object_type = ?' => 'object'])
            ->where("object_name not like '%-opt%'")
            ->orderBy('r.object_name', SORT_ASC);
        $list[''] = '(Masters - IP )';
        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = "{$row->display_name} - {$row->address}";
            if($row->object_name == $hostname){              
                $value[$row->id] = "{$row->display_name} - {$row->address}";
                return $value;
            }
        }
        return $list;
    }

    private function tramasDRUList(){
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

    private function listDRU($opt_dru){
        $id = $this->getIdDataList('druIDDataList');
        $select = (new Select())
            ->from('director_datalist_entry r')
            ->columns(['r.*'])
            ->where(['r.list_id  = ?' => $id])
            ->orderBy('r.entry_value', SORT_ASC);

        $list[''] = '(Remotes)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->entry_name] = $row->entry_value;
            if($row->entry_value == $opt_dru){
                $value[$row->entry_name] = $row->entry_value;
                return $value;
            }
        }
        return $list;
    }

    private function getIdDataList($nameList){
        $select = (new Select())
            ->from('director_datalist r')
            ->columns(['r.*'])
            ->where(['r.list_name = ?' => $nameList]);

        $row  = $this->getDb()->select($select)->fetch();

        return $row->id;
    }

    private function getDescripcion($id){
        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->where(['r.id = ?' => $id]);

        $row  = $this->getDb()->select($select)->fetch();

        return $row->name;
    }

    private function frecuenciaDMU(){
        $select = (new Select())
            ->from('rs485_frecuencia r')
            ->columns(['r.*'])
            ->orderBy('r.channel', SORT_ASC);

        $list[''] = '(select Frecuencia)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->code_hex] = $row->description;
        }
        return $list;
    }
}
