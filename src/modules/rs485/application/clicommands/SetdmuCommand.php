<?php

namespace Icinga\Module\Setdmu\Clicommands;

use Icinga\Cli\Command;

class SetdmuCommand extends Command
{
	public function dmuAction()
    {
        echo "Hello World!\n";
    }
	
	/**
	 * Say hello as someone
	 *
	 * Usage: icingacli training hello from <someone>
	 */
	public function dmufromAction()
	{
		$from = $this->params->shift();
		echo "Hello from $from!\n";
	}
}
