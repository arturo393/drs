<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Web;

use ipl\Html\Form;
use ipl\Web\Compat\CompatController;

class Controller extends CompatController
{
    protected function redirectForm(Form $form, $url)
    {
        if ($form->hasBeenSubmitted()
            && ((isset($form->valid) && $form->valid === true)
                || $form->isValid())
        ) {
            $this->redirectNow($url);
        }
    }
}
