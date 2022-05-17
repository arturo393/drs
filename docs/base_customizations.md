| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Base Customizations

## Links to device configuration

To add direct links to rs485 device configuration module, please add the following code at line 141 of the file `/usr/share/icingaweb2/modules/monitoring/application/views/scripts/partials/object/quick-actions.phtml `:

```php
    <li>
    <?php if ($object->getType() === $object::TYPE_HOST) {
            if ($object->customvars['device'] === 'dmu') {
            echo $this->qlink(
                $this->translate('Device Configuration'),
                'rs485/master/edit',
                array('host' => $object->getName()),
                array(
                    'class'             => 'action-link',
                    'data-base-target'  => '_self',
                    'icon'              => 'plug',
                    'title'             => $this->translate(
                        'Master Device Configuration'
                    )
                )
            );
	    } elseif ($object->customvars['device'] === 'dru') {
            echo $this->qlink(
                $this->translate('Device Configuration'),
                'rs485/remote/edit',
                array('host' => $object->getName()),
                array(
                    'class'             => 'action-link',
                    'data-base-target'  => '_self',
                    'icon'              => 'plug',
                    'title'             => $this->translate(
                        'Master Device Configuration'
                    )
                )
            );

	    } 
        }?>
        </li>

```


|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
