<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485;

use Icinga\Module\Rs485\Hook\ReportHook;

trait ProvidedReports
{
    public function listReports()
    {
        $reports = [];

        foreach (ReportHook::getReports() as $class => $report) {
            $reports[$class] = $report->getName();
        }

        return $reports;
    }
}
