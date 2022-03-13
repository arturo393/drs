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
     15, #15: Upstream noise switch
     16, #16: High threshold of upstream soise
     17, #17: Low threshold of upstream noise
     18, #18: Uplink noise correction value
     19, #19: Uplink noise Detection parameter 1
     20, #20: Uplink noise Detection parameter 2
     22, #22: Uplink ATT [dB]  - Cmd data 0x04004
     23, #23: Downlink ATT [dB] - Cmd data 0x04104
     25, #25: Choice of working mode - Cmd data 0xEF0B
     26, #26: Uplinkg Start Frequency
     27, #27: Downlink Start Frequency
     30  #30: Master/Slave Link Alarm Control
    ];

    public function init()
    {
        $this->setName('form_remote');
        $this->setSubmitLabel($this->translate('Enviar'));
        $this->setAction('rs485/remote/edit');
    }

    public function createElements(array $formData)
    {
        
        $listHost = $this->cargarHost();
        $listTrama = $this->tramasDRU();
        $listIdDRU = $this->listDRU();
        #$this->addDecorator('HtmlTag', array('tag' => 'fieldset', 'openOnly' => true));

        $this->addElement(
              'select',
              'host_remote',
              array(
                  'label' => $this->translate('Host'),
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
                'label' => $this->translate('Dru Id'),
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
                 'label' => $this->translate('Comando'),
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
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 40',
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
                        'label'       => $this->translate("{$descripcion}"),
                        'placeholder' => 'numero entero entre 0 - 40',
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
                    $this->addElement(
                            'select',
                            "opt{$input}",
                            array(
                                'label' => $this->translate($descripcion),
                                'multiOptions' => $listFrecuencia,
                                'required' => true,
                                // 'autosubmit' acts like an AJAX-Request
                                //'class' => 'autosubmit'
                            )
                    ); 
                    
                }
            }

            #27: Downlink Start Frequency
            if ($option == 27 ||  isset($formData['opt27_hidden'])) {
                $input = 27;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {      
                    $listFrecuencia = $this->frecuenciaDMU();         
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);                                    
                    $this->addElement(
                            'select',
                            "opt{$input}",
                            array(
                                'label' => $this->translate($descripcion),
                                'multiOptions' => $listFrecuencia,
                                'required' => true,
                                // 'autosubmit' acts like an AJAX-Request
                                //'class' => 'autosubmit'
                            )
                    );                     
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

       }       
    }

    private function cargarHost(){
            $select = (new Select())
            ->from('icinga_host r')
            ->columns(['r.*'])
            ->where(['r.object_type = ?' => 'object'])
            ->orderBy('r.object_name', SORT_ASC);
          $list[''] = '(select Host - IP )';
         foreach ($this->getDb()->select($select) as $row) {
                $list[$row->id] = "{$row->display_name} - {$row->address}";
         }
        return $list;
    }

    private function tramasDRU(){
        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->where(['r.id  in (?)' => $this->listComando])            
            ->orderBy('r.name', SORT_ASC);

        $list[''] = '(select comando)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;
        }
        return $list;
    }

    private function listDRU(){
        $id = $this->getIdDataList('druIDDataList');
        $select = (new Select())
            ->from('director_datalist_entry r')
            ->columns(['r.*'])
            ->where(['r.list_id  = ?' => $id])
            ->orderBy('r.entry_value', SORT_ASC);

        $list[''] = '(select DRU)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->entry_name] = $row->entry_value;
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
