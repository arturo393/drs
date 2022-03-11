<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;
use Icinga\Module\Rs485\Database;
use ipl\Sql\Select;

class RemoteForm extends ConfigForm
{
    use Database;

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
            ->orderBy('r.name', SORT_ASC);

        $list[''] = '(select comando)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;
        }
        return $list;
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
