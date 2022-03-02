<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485 {

    use Icinga\Application\Icinga;

    /** @var \Icinga\Application\Modules\Module $this */

    $this->provideHook('rs485/Report', '\\Icinga\\Module\\Rs485\\Reports\\SystemReport');

    $this->provideHook('rs485/Action', '\\Icinga\\Module\\Rs485\\Actions\\SendMail');

    Icinga::app()->getLoader()->registerNamespace('rs485ipl\Html', __DIR__ . '/library/vendor/ipl/Html/src');
}