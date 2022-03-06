<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Web\Forms;

use Icinga\Module\Rs485\Actions\SendMail;
use Icinga\Module\Rs485\Database;
use Icinga\Module\Rs485\ProvidedReports;
use Icinga\Module\Rs485\Report;
use Icinga\Module\Rs485\Web\Forms\Decorator\CompatDecorator;
use ipl\Web\Compat\CompatForm;

class SendForm extends CompatForm
{
    use Database;
    use ProvidedReports;

    /** @var Report */
    protected $report;

    public function setReport(Report $report)
    {
        $this->report = $report;

        return $this;
    }

    protected function assemble()
    {
        $this->setDefaultElementDecorator(new CompatDecorator());

        (new SendMail())->initConfigForm($this, $this->report);

        $this->addElement('submit', 'submit', [
            'label' => 'Send Report'
        ]);
    }

    public function onSuccess()
    {
        $values = $this->getValues();

        $sendMail = new SendMail();

        $sendMail->execute($this->report, $values);
    }
}
