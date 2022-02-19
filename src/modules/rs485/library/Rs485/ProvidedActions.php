<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485;

use Icinga\Module\Rs485\Hook\ActionHook;

trait ProvidedActions
{
    public function listActions()
    {
        $actions = [];

        foreach (ActionHook::getActions() as $class => $action) {
            $actions[$class] = $action->getName();
        }

        return $actions;
    }
}
