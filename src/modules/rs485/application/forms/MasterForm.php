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
        $listHost = $this->cargarHost();


        $this->addElement(
              'select',
              'host_remote',              
              array(
                  'label' => $this->translate('Host'),  
                  'multiple' => true,               
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
                'label' => $this->translate('Trama'),
         'multiOptions' => $listTrama,
        'required' => true,
                // 'autosubmit' acts like an AJAX-Request
                //'class' => 'autosubmit'
        )
        );



        if (isset($formData['trama']) && $formData['trama'] != '') {

            $this->addElement('text', 'cmdlength', [
                'label'       => $this->translate("{$labelCmdLength}"),
                'placeholder' => '04',
                'required' => true,
            ]);

       }


       $this->addElement('hidden', 'id_trama', null);
    }

    private function cargarHost(){
            $select = (new Select())
            ->from('icinga_host r')
            ->columns(['r.*'])
            ->where(['r.object_type = ?' => 'object'])
            ->orderBy('r.object_name', SORT_ASC);
          $list[''] = '(select Host)';
         foreach ($this->getDb()->select($select) as $row) {
                    $list[$row->address] = "{$row->object_name} - {$row->address}";
         }
        return $list;
    }

    private function tramasDMU(){
        $select = (new Select())
            ->from('rs485_dmu_trama r')
            ->columns(['r.*'])
            ->orderBy('r.name', SORT_ASC);
        $list[''] = '(select Trama)';

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

        $list[''] = '(select Trama)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;
        }
        return $list;

    }
}
