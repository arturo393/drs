| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
| ---------------------------------------------------------------------------------------------------------------------- |
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Base Customizations

## Links to device configuration

To add direct links to rs485 device configuration module, please add the following code at line 141 of the file `/usr/share/icingaweb2/modules/monitoring/application/views/scripts/partials/object/quick-actions.phtml `:

```php

        <?php if ($this->hasPermission('monitoring/command/send-custom-notification')): ?>
        <li>
            <?php if ($object->getType() === $object::TYPE_HOST) {
                echo $this->qlink(
                    $this->translate('Notification'),
                    'monitoring/host/send-custom-notification',
                    array('host' => $object->getName()),
                    array(
                        'class' => 'action-link',
                        'data-base-target' => '_self',
                        'icon' => 'bell',
                        'title' => $this->translate(
                            'Send a custom notification to contacts responsible for this host'
                        )
                    )
                );
            } else {
                echo $this->qlink(
                    $this->translate('Notification'),
                    'monitoring/service/send-custom-notification',
                    array('host' => $object->getHost()->getName(), 'service' => $object->getName()),
                    array(
                        'class' => 'action-link',
                        'data-base-target' => '_self',
                        'icon' => 'bell',
                        'title' => $this->translate(
                            'Send a custom notification to contacts responsible for this service'
                        )
                    )
                );
            } ?>
        </li>
        <?php endif ?>
        <?php if ($this->hasPermission('monitoring/command/downtime/schedule')): ?>
        <li>
            <?php if ($object->getType() === $object::TYPE_HOST) {
                echo $this->qlink(
                    $this->translate('Downtime'),
                    'monitoring/host/schedule-downtime',
                    array('host' => $object->getName()),
                    array(
                        'class' => 'action-link',
                        'data-base-target' => '_self',
                        'icon' => 'plug',
                        'title' => $this->translate(
                            'Schedule a downtime to suppress all problem notifications within a specific period of time'
                        )
                    )
                );
            } else {
                echo $this->qlink(
                    $this->translate('Downtime'),
                    'monitoring/service/schedule-downtime',
                    array('host' => $object->getHost()->getName(), 'service' => $object->getName()),
                    array(
                        'class' => 'action-link',
                        'data-base-target' => '_self',
                        'icon' => 'plug',
                        'title' => $this->translate(
                            'Schedule a downtime to suppress all problem notifications within a specific period of time'
                        )
                    )
                );
            } ?>
        </li>
        <?php endif ?>
        <?php if ($this->hasPermission('rs485/master/edit')): ?>

        <li>
            <?php if ($object->getType() === $object::TYPE_HOST) {
                if (substr($object->host, 5, 3) === 'opt') {
                    echo $this->qlink(
                        $this->translate('Device Configuration'),
                        'rs485/remote/edit',
                        array('host' => $object->getName()),
                        array(
                            'class' => 'action-link',
                            'data-base-target' => '_self',
                            'icon' => 'plug',
                            'title' => $this->translate(
                                'Remote Device Configuration'
                            )
                        )
                    );
                 } //elseif (substr($object->host, 0, 3) === 'dmu') {
                //     echo $this->qlink(
                //         $this->translate('Device Configuration'),
                //         'rs485/master/edit',
                //         array('host' => $object->getName()),
                //         array(
                //             'class' => 'action-link',
                //             'data-base-target' => '_self',
                //             'icon' => 'plug',
                //             'title' => $this->translate(
                //                 'Master Device Configuration'
                //             )
                //         )
                //     );
                // }
            } else {
                if (substr($object->service, 0, 6) === 'Master' ) {
                    
                    $frequency = isset($object->customvars['frequencies']) ? $object->customvars['frequencies'] :" " ;
                    $service = $object->host->getName() . '-freq' . $frequency;
                    echo $this->qlink(
                        $this->translate('Device Configuration'),
                        'rs485/master/edit',
                        array('host' => $object->host->getName(),'freq'=> $frequency),
                        array(
                            'class' => 'action-link',
                            'data-base-target' => '_self',
                            'icon' => 'plug',
                            'title' => $this->translate(
                                'Master Device Configuration'
                            )
                        )
                    );
                } else if (isset($object->customvars['opt']) && $object->customvars['dru']) {
                    $opt = $object->customvars['opt'];
                    $dru = $object->customvars['dru'];
                    $service = $object->host->getName() . '-opt' . $opt . '-dru' . $dru;
                    echo $this->qlink(
                        $this->translate('Device Configuration'),
                        'rs485/remote/edit',
                        array('service' => $service),
                        array(
                            'class' => 'action-link',
                            'data-base-target' => '_self',
                            'icon' => 'plug',
                            'title' => $this->translate(
                                'Remote Device Configuration'
                            )
                        )
                    );
                }
            }
            ?>
            <?php endif ?>
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
