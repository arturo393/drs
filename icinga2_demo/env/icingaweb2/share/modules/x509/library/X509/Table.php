<?php
// Icinga Web 2 X.509 Module | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\X509;

use ipl\Html\BaseHtmlElement;
use ipl\Html\Html;

class Table extends BaseHtmlElement
{
    protected $tag = 'table';

    protected $rows = [];

    public function addRow(array $cells, $attributes = null)
    {
        $row = Html::tag('tr', $attributes);

        foreach ($cells as $cell) {
            $row->add(Html::tag('td', $cell));
        }

        $this->rows[] = $row;
    }

    public function renderContent()
    {
        $tbody = Html::tag('tbody');

        foreach ($this->rows as $row) {
            $tbody->add($row);
        }

        $this->add($tbody);

        return parent::renderContent(); // TODO: Change the autogenerated stub
    }
}
