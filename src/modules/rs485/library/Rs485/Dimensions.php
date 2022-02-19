<?php
// Icinga Rs485 | (c) 2018 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485;

trait Dimensions
{
    protected $dimensions;

    public function getDimensions()
    {
        return $this->dimensions;
    }

    public function setDimensions(array $dimensions)
    {
        $this->dimensions = $dimensions;

        return $this;
    }
}
