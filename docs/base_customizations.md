| ![Sigma Telecom](/docs/logo-sigma.svg)                                                                                 |
|------------------------------------------------------------------------------------------------------------------------|
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |

# Base Customizations

## Links to device configuration

To add direct links to rs485 device configuration module, please add the following code at line 141 of the
file `/usr/share/icingaweb2/modules/monitoring/application/views/scripts/partials/object/quick-actions.phtml `:

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
                 } 
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
            <?php if ($this->hasPermission('rs485/master/edit')): ?>                         
            <li>   
               <?php if ($object->getType() === $object::TYPE_HOST) { 
               $linkAddress = $object->address; 
               echo "<a href=\"http://$linkAddress\" target='_blank'>Configuration</a>"; 
               }            
               ?> 
               <?php endif ?> 
           </li>  
        </li>
    </ul>
</div>

```

## To not show feature commands in services tables (Because its not working ) , if want show this uncomment the line 55.

Please comment the line 55 or replace the following code at line 55 to the
file `/usr/share/icingaweb2/modules/monitoring/application/views/scripts/partials/object/detail-content.phtml `:

```php 

<!-- <?= $this->render('show/components/flags.phtml') ?> -->

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

## Remove Custom Variables and Feature Commands

edit /etc/icingaweb2/enabledModules/monitoring/application/views/scripts/show/components/flags.phtml

```
<div class="content" data-base-target="_next">
<?= $this->render('show/components/output.phtml') ?>
<?= $this->render('show/components/grapher.phtml') ?>
<?= $this->render('show/components/extensions.phtml') ?>

<h2><?= $this->translate('Problem handling') ?></h2>
<table class="name-value-table">
<tbody>
<?= $this->render('show/components/acknowledgement.phtml') ?>
<?= $this->render('show/components/comments.phtml') ?>
<?= $this->render('show/components/downtime.phtml') ?>
<?= $this->render('show/components/notes.phtml') ?>
<?= $this->render('show/components/actions.phtml') ?>
<?= $this->render('show/components/flapping.phtml') ?>
<?php if ($object->type === 'service'): ?>
<?= $this->render('show/components/servicegroups.phtml') ?>
<?php else: ?>
<?= $this->render('show/components/hostgroups.phtml') ?>
<?php endif ?>
</tbody>
</table>

<?= $this->render('show/components/perfdata.phtml') ?>

<h2><?= $this->translate('Notifications') ?></h2>
<table class="name-value-table">
<tbody>
<?= $this->render('show/components/notifications.phtml') ?>
<?php if ($this->hasPermission('*') || ! $this->hasPermission('no-monitoring/contacts')): ?>
<?= $this->render('show/components/contacts.phtml') ?>
<?php endif ?>
</tbody>
</table>

<h2><?= $this->translate('Check execution') ?></h2>
<table class="name-value-table">
<tbody>
<?= $this->render('show/components/command.phtml') ?>
<?= $this->render('show/components/checksource.phtml') ?>
<?= $this->render('show/components/reachable.phtml') ?>
<?= $this->render('show/components/checkstatistics.phtml') ?>
<?= $this->render('show/components/checktimeperiod.phtml') ?>
</tbody>
</table>
<!--
<?php if (! empty($object->customvars)): ?>
<h2><?= $this->translate('Custom Variables') ?></h2>
<table id="<?= $object->type ?>-customvars" class="name-value-table collapsible" data-visible-height="200">
<tbody>
<?= $this->render('show/components/customvars.phtml') ?>
</tbody>
</table>
<?php endif ?>

<?= $this->render('show/components/flags.phtml') ?>
-->
</div>
  ```

# Edit left menu:

edit this file for custom lef menu
vim /etc/icingaweb2/enabledModules/monitoring/configuration.php

# Edit about page

  ```
'/usr/share/icingaweb2/application/views/scripts/about/index.phtml'
  ```

with

  ```
src/base_customization/index.phtml
  ```

copy uqomm image

  ```
 image with src/base_customization/LOGOS6.png 
  ```

to

  ```
/usr/share/icingaweb2/public/img
  ```

~               
| |
|------------------------------------------------------------------------------------------------------------------------|
| [Readme](/readme.md) - [Master Node](/docs/setup_master_debian.md) - [Satellite Node](/docs/setup_satellite_debian.md) |
