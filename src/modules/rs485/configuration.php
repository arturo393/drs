<?php

use Icinga\Application\Version;

    /** @var \Icinga\Application\Modules\Module $this */

    $this->provideCssFile('system-report.css');

    if (version_compare(Version::VERSION, '2.9.0', '<')) {
        $this->provideJsFile('vendor/flatpickr.min.js');
        $this->provideCssFile('vendor/flatpickr.min.css');
    }

    /*$this->menuSection(N_('Device configuration'))->add(N_('Config DRU'), array(
        'url' => 'rs485/setdru/list',
    ));

    $this->menuSection(N_('Device configuration'))->add(N_('Config DMU'), array(
        'url' => 'rs485/setdmu/list',
    ));

    $this->menuSection(N_('Device configuration'))->add(N_('Formulario General'), array(
        'url' => 'rs485/general/edit',
    ));*/

    $this->menuSection(N_('Device configuration'))->add(N_('Config Master'), array(
        'url' => 'rs485/master/edit',
    ));

    $this->menuSection(N_('Device configuration'))->add(N_('Config Remote'), array(
        'url' => 'rs485/remote/edit',
    ));

   /*$this->provideConfigTab('form', array(
        'title' => $this->translate('Formulario para ingresar datos dmu'),
        'label' => $this->translate('Formulario DMU'),
        'url'   => 'rs485/setdmu/dmu'
    ));
 

    $this->provideConfigTab('form', array(
        'title' => $this->translate('Formulario para ingresar datos dru'),
	'label' => $this->translate('Formulario DRU'),
	'url'   => 'rs485/setdru/dru'
    ));*/

    $this->provideConfigTab('backend', array(
        'title' => $this->translate('Configure the database backend'),
        'label' => $this->translate('Backend'),
        'url'   => 'config/backend'
    ));
    