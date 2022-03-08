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
        $this->setSubmitLabel($this->translate('Enviar'));
        $this->setAction('rs485/master/edit');
    }

    public function createElements(array $formData)
    {
        $this->addDecorator('HtmlTag', array('tag' => 'fieldset', 'openOnly' => true));
        $listHost = $this->cargarHost();
        $listTrama = $this->tramasDMU();

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

            if ($option == 1 ||  isset($formData["opt1_hidden"])) {
                $input = 1;
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
                            '01' => 'Channel',
                            '02' => 'WideBand'
                            ],
                            'required' => true,
                            // 'autosubmit' acts like an AJAX-Request
                            //'class' => 'autosubmit'
                        )
                    ); 
                }    
            }

            if ($option == 2 ||  isset($formData['opt2_hidden']) ) {
                $input = 2;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {   
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('text', "opt{$input}_1", [
                        'label'       => $this->translate("{$descripcion} - Uplink ATT [dB]"),
                        'placeholder' => 'entero en 0 - 40',
                        'required' => true,
                    ]); 
                    
                    $this->addElement('text', "opt{$input}_2", [
                        'label'       => $this->translate("{$descripcion} - Downlink ATT [dB]"),
                        'placeholder' => 'entero en 0 - 40',
                        'required' => true,                        
                         
                    ]);
                }

            }

            if ($option == 3 ||  isset($formData['opt3_hidden'])) {
                $input = 3;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {               
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    for ($i=1; $i<=16; $i++){
                        $this->addElement('checkbox', "opt{$input}_{$i}", [
                            'label'       => $this->translate("{$descripcion} - Channel {$i}")
                        ]);
                    }
                }

            }

            if ($option == 4 ||  isset($formData['opt4_hidden'])) {
                $input = 4;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {      
                    $listFrecuencia = $this->frecuenciaDMU();         
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    for ($i=1; $i<=16; $i++){
                        $this->addElement('checkbox', "opt{$input}_{$i}", [
                            'label'       => $this->translate("{$descripcion} - Channel {$i}")
                        ]);
                        $this->addElement(
                            'select',
                            "opt{$input}_{$i}",
                            array(
                                'label' => $this->translate("{$descripcion} - Channel {$i}"),
                                'multiOptions' => $listFrecuencia,
                                'required' => true,
                                // 'autosubmit' acts like an AJAX-Request
                                //'class' => 'autosubmit'
                            )
                        ); 
                    }
                }

            }

            if ($option == 5 ||  isset($formData['opt5_hidden'])) {
                $input = 5;
                $hidden =  isset($formData["opt{$input}_hidden"]) ? $formData["opt{$input}_hidden"] : 0;
                if ($option != $hidden) {               
                    $this->addElement('hidden', "opt{$input}_hidden", ['value' => $input]);
                    $descripcion = $this->getDescripcion($input);
                    $this->addElement('checkbox', "opt{$input}_1", [
                        'label'       => $this->translate("{$descripcion} - Port 1")
                    ]); 
                    
                    $this->addElement('checkbox', "opt{$input}_2", [
                        'label'       => $this->translate("{$descripcion} - Port 2")
                    ]); 

                    $this->addElement('checkbox', "opt{$input}_3", [
                        'label'       => $this->translate("{$descripcion} - Port 3")
                    ]); 

                    $this->addElement('checkbox', "opt{$input}_4", [
                        'label'       => $this->translate("{$descripcion} - Port 4")
                    ]);                     
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

    private function tramasDMU(){
        $select = (new Select())
            ->from('rs485_dmu_trama r')
            ->columns(['r.*'])
            //->where(['r.id not in (?)' => $excluir])
            ->orderBy('r.name', SORT_ASC);
        $list[''] = '(select comando)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;
        }
        return $list;
    }

    private function tramasDRU(){
        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->orderBy('r.name', SORT_ASC);

        $list[''] = '(select comando)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;
        }
        return $list;
    }

    private function getDescripcion($id){
        $select = (new Select())
            ->from('rs485_dmu_trama r')
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
