<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;
use Icinga\Module\Rs485\Database;
use ipl\Sql\Select;

class SetdmuForm extends ConfigForm
{
    use Database;	
	
    public function init()
    {
        $this->setName('form_dmu');
	$this->setSubmitLabel($this->translate('Enviar Trama'));
        $this->setAction('rs485/setdmu/save');
    }

    public function createElements(array $formData)
    {
	    $listHost = $this->cargarHost();
	
        $this->addElement(
              'select',
              'host_remote',
              array(
                  'label' => $this->translate('Host'),
		  'multiOptions' => $listHost ,
		  'required' => true,
                  // 'autosubmit' acts like an AJAX-Request
                  //'class' => 'autosubmit'
	      )
          );   
	   
	   
         $this->addElement('text', 'user_remote', [
            'label'       => $this->translate('Usuario'),
	    'placeholder' => 'user',
	    'required' => true,
        ]);

        $this->addElement('password', 'password_remote', [
            'label'       => $this->translate('Contraseña'),
	    'placeholder' => '......',
	    'required' => true,
        ]);        
        

        $this->addElement('text', 'dmu_cmdlength', [
            'label'       => $this->translate('CMD Length'),
	    'placeholder' => '04',
	    'required' => true,
        ]);
	
	    $this->addElement('text', 'dmu_cmddata', [
            'label'       => $this->translate('CMD Data'),
	    'placeholder' => '00FF01',
	    'required' => true,
	    ]);

	    $this->addElement('hidden', 'id', null);
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
}

