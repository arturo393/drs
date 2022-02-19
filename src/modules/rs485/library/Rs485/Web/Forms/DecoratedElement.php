<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Web\Forms;

use ipl\Html\Contract\FormElementDecorator;

trait DecoratedElement
{
    protected function addDecoratedElement(FormElementDecorator $decorator, $type, $name, array $attributes)
    {
        $element = $this->createElement($type, $name, $attributes);
        $decorator->decorate($element);
        $this->registerElement($element);
        $this->add($element);
    }
}
