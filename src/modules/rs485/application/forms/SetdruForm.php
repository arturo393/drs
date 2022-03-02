<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;

class SetdruForm extends ConfigForm
{
    public function init()
    {
        $this->setName('form_dru');
	$this->setSubmitLabel($this->translate('Enviar Trama'));
        $this->setAction('rs485/setdru/save');
    }

    public function createElements(array $formData)
    {
        $this->addElement('text', 'user_remote', [
            'label'       => $this->translate('Usuario'),
            'placeholder' => 'user'
        ]);

        $this->addElement('password', 'password_remote', [
            'label'       => $this->translate('Contraseña'),
            'placeholder' => '......'
        ]); 
        
        
        $this->addElement('text', 'host_remote', [
            'label'       => $this->translate('Host'),
            'placeholder' => '192.168.60.78'
        ]);        
        
        $this->addElement('text', 'dru_cmdlength', [
            'label'       => $this->translate('CMD Length'),
            'placeholder' => '04'
        ]);

        $this->addElement('text', 'dru_cmdcode', [
            'label'       => $this->translate('CMD Code'),
            'placeholder' => 'EF'
        ]);

        $this->addElement('text', 'dru_cmddata', [
            'label'       => $this->translate('CMD Data'),
            'placeholder' => '00FF01'
	    ]);

	    $this->addElement('hidden', 'id', null);
    }
}

