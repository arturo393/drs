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

