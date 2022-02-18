<?php
// Icinga Reporting | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Controllers;

use Icinga\Application\Config;
use Icinga\Module\Rs485\Forms\SelectBackendForm;
use Icinga\Web\Controller;

class ConfigController extends Controller
{
    public function init()
    {
        $this->assertPermission('config/modules');

        parent::init();
    }

    public function backendAction()
    {
        $form = (new SelectBackendForm())
            ->setIniConfig(Config::module('rs485'));

        $form->handleRequest();

        $this->view->tabs = $this->Module()->getConfigTabs()->activate('backend');
        $this->view->form = $form;
    }

}
