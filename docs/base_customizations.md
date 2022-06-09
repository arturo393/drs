| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Base Customizations

## Links to device configuration

To add direct links to rs485 device configuration module, please add the following code at line 141 of the file `/usr/share/icingaweb2/modules/monitoring/application/views/scripts/partials/object/quick-actions.phtml `:

```php
    <li>
    <?php 
     if (substr($object->host,5,3) === 'opt') {
            echo $this->qlink(
                $this->translate('Device Configuration'),
                'rs485/remote/edit',
                array('host' => $object->getName()),
                array(
                    'class'             => 'action-link',
                    'data-base-target'  => '_self',
                    'icon'              => 'plug',
                    'title'             => $this->translate(
                        'Remote Device Configuration'
                    )
                )
            );

	    } elseif ($object->getType() === $object::TYPE_HOST) {
            if (substr($object->host,0,3) === 'dmu') {
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
	    }
        }?>
        </li>

```

## Change Tab Icon 
```
cp -R /tmp/sigma-rds/src/modules/icingaweb2-theme-sigma/public/img/favicon.png /usr/share/icingaweb2/public/img/
chown www-data:icingaweb2 /usr/share/icingaweb2/modules/sigma-theme
```

## Change Tab name
```
sed -i 's/Icinga Web/DRS/g' /usr/share/php/Icinga/Web/Controller/ActionController.php
sed -i 's/Icinga Web/DRS/g' /usr/share/icingaweb2/application/controllers/AuthenticationController.php

```

|                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
