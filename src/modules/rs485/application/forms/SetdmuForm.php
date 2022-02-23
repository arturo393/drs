<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;

class SetdmuForm extends ConfigForm
{
    public function init()
    {
        $this->setName('form_dmu');
	$this->setSubmitLabel($this->translate('Enviar Trama'));
        $this->setAction('rs485/setdmu/save');
    }

    public function createElements(array $formData)
    {
        $this->addElement('text', 'dmu_cmdlength', [
            'label'       => $this->translate('CMD Length'),
            'placeholder' => '04'
        ]);
	
	$this->addElement('text', 'dmu_cmddata', [
            'label'       => $this->translate('CMD Data'),
            'placeholder' => '00FF01'
	]);

	$this->addElement('hidden', 'id', null);
    }
}

