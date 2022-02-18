<?php

use Icinga\Application\Version;

    /** @var \Icinga\Application\Modules\Module $this */

    $this->provideCssFile('system-report.css');

    if (version_compare(Version::VERSION, '2.9.0', '<')) {
        $this->provideJsFile('vendor/flatpickr.min.js');
        $this->provideCssFile('vendor/flatpickr.min.css');
    }

    $this->menuSection(N_('Rs485'))->add(N_('Config DRU'), array(
        'url' => 'rs485/setdru/list',
    ));

    

    $this->provideConfigTab('form', array(
        'title' => $this->translate('Formulario para ingresar datos dru'),
	'label' => $this->translate('Formulario DRU'),
	'url'   => 'rs485/setdru/dru'
    ));

    $this->provideConfigTab('backend', array(
        'title' => $this->translate('Configure the database backend'),
        'label' => $this->translate('Backend'),
        'url'   => 'config/backend'
    ));


/*
$this->menuSection('RS485')
     ->add('Configurar DMU')
     ->setUrl('rs485/reporte/francis');

$this->menuSection('RS485')
     ->add('Hello World')
     ->setUrl('rs485/hello/world');

$this->menuSection('RS485')
     ->add('Hello dmu')
     ->setUrl('rs485/setdru/list');

$this->menuSection('RS485')
     ->add('Configurar DRU')
     ->setUrl('rs485/setdru/dru');
*/
