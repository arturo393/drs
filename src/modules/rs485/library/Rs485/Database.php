<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485;

use Icinga\Application\Config;
use Icinga\Data\ResourceFactory;
use ipl\Sql;

trait Database
{
    protected function getDb($resource = null)
    {
        $config = new Sql\Config(ResourceFactory::getResourceConfig(
            $resource ?: Config::module('rs485')->get('backend', 'resource', 'rs485')
        ));

        $config->options = [
            \PDO::ATTR_DEFAULT_FETCH_MODE   => \PDO::FETCH_OBJ,
            \PDO::MYSQL_ATTR_INIT_COMMAND   => "SET SESSION SQL_MODE='STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE"
                . ",ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'"
        ];

        $conn = new RetryConnection($config);

        return $conn;
    }

    protected function listTimeframes()
    {
        $select = (new Sql\Select())
            ->from('timeframe')
            ->columns(['id', 'name']);

        $timeframes = [];

        foreach ($this->getDb()->select($select) as $row) {
            $timeframes[$row->id] = $row->name;
        }

        return $timeframes;
    }

    protected function listTemplates()
    {
        $select = (new Sql\Select())
            ->from('template')
            ->columns(['id', 'name']);

        $templates = [];

        foreach ($this->getDb()->select($select) as $row) {
            $templates[$row->id] = $row->name;
        }

        return $templates;
    }
}
