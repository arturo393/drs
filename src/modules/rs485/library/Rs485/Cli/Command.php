<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Cli;

use Icinga\Application\Icinga;
use Icinga\Application\Version;
use Icinga\Module\Rs485\Database;

class Command extends \Icinga\Cli\Command
{
    use Database;

    // Fix Web 2 issue where $configs is not properly initialized
    protected $configs = [];

    public function init()
    {
        if (version_compare(Version::VERSION, '2.7.0', '<')) {
            Icinga::app()->getModuleManager()->loadEnabledModules();
        }
    }
}
