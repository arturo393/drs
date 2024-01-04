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
``
vim /usr/share/icingaweb2/modules/monitoring/configuration.php
``
whith this file

 ```
/* Icinga Web 2 | (c) 2014 Icinga Development Team | GPLv2+ */

use Icinga\Authentication\Auth;

/** @var $this \Icinga\Application\Modules\Module */

$this->providePermission(
    'monitoring/command/*',
    $this->translate('Allow all commands')
);
$this->providePermission(
    'monitoring/command/schedule-check',
    $this->translate('Allow scheduling host and service checks')
);
$this->providePermission(
    'monitoring/command/schedule-check/active-only',
    $this->translate('Allow scheduling host and service checks (Only on objects with active checks enabled)')
);
$this->providePermission(
    'monitoring/command/acknowledge-problem',
    $this->translate('Allow acknowledging host and service problems')
);
$this->providePermission(
    'monitoring/command/remove-acknowledgement',
    $this->translate('Allow removing problem acknowledgements')
);
$this->providePermission(
    'monitoring/command/comment/*',
    $this->translate('Allow adding and deleting host and service comments')
);
$this->providePermission(
    'monitoring/command/comment/add',
    $this->translate('Allow commenting on hosts and services')
);
$this->providePermission(
    'monitoring/command/comment/delete',
    $this->translate('Allow deleting host and service comments')
);
$this->providePermission(
    'monitoring/command/downtime/*',
    $this->translate('Allow scheduling and deleting host and service downtimes')
);
$this->providePermission(
    'monitoring/command/downtime/schedule',
    $this->translate('Allow scheduling host and service downtimes')
);
$this->providePermission(
    'monitoring/command/downtime/delete',
    $this->translate('Allow deleting host and service downtimes')
);
$this->providePermission(
    'monitoring/command/process-check-result',
    $this->translate('Allow processing host and service check results')
);
$this->providePermission(
    'monitoring/command/feature/instance',
    $this->translate('Allow processing commands for toggling features on an instance-wide basis')
);
$this->providePermission(
    'monitoring/command/feature/object/*',
    $this->translate('Allow processing commands for toggling features on host and service objects')
);
$this->providePermission(
    'monitoring/command/feature/object/active-checks',
    $this->translate('Allow processing commands for toggling active checks on host and service objects')
);
$this->providePermission(
    'monitoring/command/feature/object/passive-checks',
    $this->translate('Allow processing commands for toggling passive checks on host and service objects')
);
$this->providePermission(
    'monitoring/command/feature/object/notifications',
    $this->translate('Allow processing commands for toggling notifications on host and service objects')
);
$this->providePermission(
    'monitoring/command/feature/object/event-handler',
    $this->translate('Allow processing commands for toggling event handlers on host and service objects')
);
$this->providePermission(
    'monitoring/command/feature/object/flap-detection',
    $this->translate('Allow processing commands for toggling flap detection on host and service objects')
);
$this->providePermission(
    'monitoring/command/send-custom-notification',
    $this->translate('Allow sending custom notifications for hosts and services')
);
$this->providePermission(
    'no-monitoring/contacts',
    $this->translate('Prohibit access to contacts and contactgroups')
);

$this->provideRestriction(
    'monitoring/filter/objects',
    $this->translate('Restrict views to the Icinga objects that match the filter')
);
$this->provideRestriction(
    'monitoring/blacklist/properties',
    $this->translate('Hide the properties of monitored objects that match the filter')
);

$this->provideConfigTab('backends', array(
    'title' => $this->translate('Configure how to retrieve monitoring information'),
    'label' => $this->translate('Backends'),
    'url' => 'config'
));
$this->provideConfigTab('security', array(
    'title' => $this->translate('Configure how to protect your monitoring environment against prying eyes'),
    'label' => $this->translate('Security'),
    'url' => 'config/security'
));
$this->provideSetupWizard('Icinga\Module\Monitoring\MonitoringWizard');

/*
 * Available Search Urls
 */
$this->provideSearchUrl($this->translate('Tactical Overview'), 'monitoring/tactical', 100);
$this->provideSearchUrl($this->translate('Hosts'), 'monitoring/list/hosts?sort=host_severity&limit=10', 99);
$this->provideSearchUrl($this->translate('Services'), 'monitoring/list/services?sort=service_severity&limit=10', 98);
$this->provideSearchUrl($this->translate('Hostgroups'), 'monitoring/list/hostgroups?limit=10', 97);
$this->provideSearchUrl($this->translate('Servicegroups'), 'monitoring/list/servicegroups?limit=10', 96);

/*
 * Available navigation items
 */
$this->provideNavigationItem('host-action', $this->translate('Host Action'));
$this->provideNavigationItem('service-action', $this->translate('Service Action'));
// Notes are disabled as we're not sure whether to really make a difference between actions and notes
//$this->provideNavigationItem('host-note', $this->translate('Host Note'));
//$this->provideNavigationItem('service-note', $this->translate('Service Note'));

/*
 * Problems Section
 */
$section = $this->menuSection(N_('Problems'), array(
    'renderer' => array(
        'SummaryNavigationItemRenderer',
        'state' => 'critical'
    ),
    'icon'      => 'attention-circled',
    'priority'  => 20
));
$section->add(N_('Host Problems'), array(
    'icon'        => 'host',
    'description' => $this->translate('List current host problems'),
    'renderer'    => array(
        'MonitoringBadgeNavigationItemRenderer',
        'columns' => array(
            'hosts_down_unhandled' => $this->translate('%d unhandled hosts down')
        ),
        'state'    => 'critical',
        'dataView' => 'unhandledhostproblems'
    ),
    'url'       => 'monitoring/list/hosts?host_problem=1&sort=host_severity',
    'priority'  => 50
));
$section->add(N_('Service Problems'), array(
    'icon'        => 'service',
    'description' => $this->translate('List current service problems'),
    'renderer'    => array(
        'MonitoringBadgeNavigationItemRenderer',
        'columns' => array(
            'services_critical_unhandled' => $this->translate('%d unhandled services critical')
        ),
        'state'    => 'critical',
        'dataView' => 'unhandledserviceproblems'
    ),
    'url'       => 'monitoring/list/services?service_problem=1&sort=service_severity&dir=desc',
    'priority'  => 60
));
$section->add(N_('Service Grid'), array(
    'icon'        => 'services',
    'description' => $this->translate('Display service problems as grid'),
    'url'         => 'monitoring/list/servicegrid?problems',
    'priority'    => 70
));
#$section->add(N_('Current Downtimes'), array(
#    'icon'        => 'plug',
#    'description' => $this->translate('List current downtimes'),
#    'url'         => 'monitoring/list/downtimes?downtime_is_in_effect=1',
#    'priority'    => 80
#));

/*
 * Overview Section
 */
$section = $this->menuSection(N_('Overview'), array(
    'icon'      => 'binoculars',
    'priority'  => 30
));
$section->add(N_('Tactical Overview'), array(
    'icon'        => 'chart-pie',
    'description' => $this->translate('Open tactical overview'),
    'url'         => 'monitoring/tactical',
    'priority'    => 40
));
$section->add(N_('Hosts'), array(
    'icon'        => 'host',
    'description' => $this->translate('List hosts'),
    'url'         => 'monitoring/list/hosts',
    'priority'    => 50
));
$section->add(N_('Services'), array(
    'icon'        => 'service',
    'description' => $this->translate('List services'),
    'url'         => 'monitoring/list/services',
    'priority'    => 50
));
#$section->add(N_('Servicegroups'), array(
#    'icon'        => 'services',
#    'description' => $this->translate('List service groups'),
#    'url'         => 'monitoring/list/servicegroups',
#    'priority'    => 60
#));
#$section->add(N_('Hostgroups'), array(
#    'icon'        => 'host',
#    'description' => $this->translate('List host groups'),
#    'url'         => 'monitoring/list/hostgroups',
#    'priority'    => 60
#));

// Checking the permission here since navigation items don't support negating permissions
$auth = Auth::getInstance();
if ($auth->hasPermission('*') || ! $auth->hasPermission('no-monitoring/contacts')) {
    $section->add(N_('Contacts'), array(
        'icon'        => 'user',
        'description' => $this->translate('List contacts'),
        'url'         => 'monitoring/list/contacts',
        'priority'    => 70
    ));
#    $section->add(N_('Contactgroups'), array(
#        'icon'        => 'users',
#        'description' => $this->translate('List users'),
#        'url'         => 'monitoring/list/contactgroups',
#        'priority'    => 70
#    ));
}

#$section->add(N_('Comments'), array(
#    'icon'        => 'chat-empty',
#    'description' => $this->translate('List comments'),
#    'url'         => 'monitoring/list/comments?comment_type=comment|comment_type=ack',
#    'priority'    => 80
#));
#$section->add(N_('Downtimes'), array(
#    'icon'        => 'plug',
#    'description' => $this->translate('List downtimes'),
#    'url'         => 'monitoring/list/downtimes',
#    'priority'    => 80
#));

/*
 * History Section
 */
$section = $this->menuSection(N_('History'), array(
    'icon'      => 'history',
    'priority'  => 90
));
$section->add(N_('Event Grid'), array(
    'icon'        => 'history',
    'description' => $this->translate('Open event grid'),
    'priority'    => 10,
    'url'         => 'monitoring/list/eventgrid'
));
$section->add(N_('Event Overview'), array(
    'icon'        => 'history',
    'description' => $this->translate('Open event overview'),
    'priority'    => 20,
    'url'         => 'monitoring/list/eventhistory?timestamp>=-7%20days'
));
$section->add(N_('Notifications'), array(
    'icon'        => 'bell',
    'description' => $this->translate('List notifications'),
    'priority'    => 30,
    'url'         => 'monitoring/list/notifications?notification_timestamp>=-7%20days',
));
$section->add(N_('Timeline'), array(
    'icon'        => 'clock',
    'description' => $this->translate('Open timeline'),
    'priority'    => 40,
    'url'         => 'monitoring/timeline'
));

/*
 * Reporting Section
 */
$section = $this->menuSection(N_('Reporting'), array(
    'icon'      => 'barchart',
    'priority'  => 100
));

/*
 * System Section
 */
$section = $this->menuSection(N_('System'));
$section->add(N_('Monitoring Health'), array(
    'icon'        => 'check',
    'description' => $this->translate('Open monitoring health'),
    'url'         => 'monitoring/health/info',
    'priority'    => 720,
    'renderer'    => 'BackendAvailabilityNavigationItemRenderer'
));

/*
 * Current Incidents
 */
$dashboard = $this->dashboard(N_('Current Incidents'), array('priority' => 50));
$dashboard->add(
    N_('Service Problems'),
    'monitoring/list/services?service_problem=1&limit=10&sort=service_severity',
    100
);
$dashboard->add(
    N_('Recently Recovered Services'),
    'monitoring/list/services?service_state=0&limit=10&sort=service_last_state_change&dir=desc',
    110
);
$dashboard->add(
    N_('Host Problems'),
    'monitoring/list/hosts?host_problem=1&sort=host_severity',
    120
);

/*
 * Overview
 */
//$dashboard = $this->dashboard(N_('Overview'), array('priority' => 60));
//$dashboard->add(
//    N_('Service Grid'),
//    'monitoring/list/servicegrid?limit=15,18'
//);
//$dashboard->add(
//    N_('Service Groups'),
//    'monitoring/list/servicegroups'
//);
//$dashboard->add(
//    N_('Host Groups'),
//    'monitoring/list/hostgroups'
//);

/*
 * Most Overdue
 */
/*
$dashboard = $this->dashboard(N_('Overdue'), array('priority' => 70));
$dashboard->add(
    N_('Late Host Check Results'),
    'monitoring/list/hosts?host_next_update<now',
    100
);
$dashboard->add(
    N_('Late Service Check Results'),
    'monitoring/list/services?service_next_update<now',
    110
);
$dashboard->add(
    N_('Acknowledgements Active For At Least Three Days'),
    'monitoring/list/comments?comment_type=Ack&comment_timestamp<-3 days&sort=comment_timestamp&dir=asc',
    120
);
$dashboard->add(
    N_('Downtimes Active For More Than Three Days'),
    'monitoring/list/downtimes?downtime_is_in_effect=1&downtime_scheduled_start<-3%20days&sort=downtime_start&dir=asc',
    130
);
 */
/*
 * Muted Objects
 */
/*
$dashboard = $this->dashboard(N_('Muted'), array('priority' => 80));
$dashboard->add(
    N_('Disabled Service Notifications'),
    'monitoring/list/services?service_notifications_enabled=0&limit=10',
    100
);
$dashboard->add(
    N_('Disabled Host Notifications'),
    'monitoring/list/hosts?host_notifications_enabled=0&limit=10',
    110
);
$dashboard->add(
    N_('Disabled Service Checks'),
    'monitoring/list/services?service_active_checks_enabled=0&limit=10',
    120
);
$dashboard->add(
    N_('Disabled Host Checks'),
    'monitoring/list/hosts?host_active_checks_enabled=0&limit=10',
    130
);
$dashboard->add(
    N_('Acknowledged Problem Services'),
    'monitoring/list/services?service_acknowledgement_type!=0&service_problem=1&sort=service_state&limit=10',
    140
);
$dashboard->add(
    N_('Acknowledged Problem Hosts'),
    'monitoring/list/hosts?host_acknowledgement_type!=0&host_problem=1&sort=host_severity&limit=10',
    150
);
 */
/*
 * Activity Stream
 */
//$dashboard = $this->dashboard(N_('Activity Stream'), array('priority' => 90));
//$dashboard->add(
//    N_('Recent Events'),
//    'monitoring/list/eventhistory?timestamp>=-3%20days&sort=timestamp&dir=desc&limit=8'
//);
//$dashboard->add(
//    N_('Recent Hard State Changes'),
//    'monitoring/list/eventhistory?timestamp>=-3%20days&type=hard_state&sort=timestamp&dir=desc&limit=8'
//);
//$dashboard->add(
//    N_('Recent Notifications'),
//    'monitoring/list/eventhistory?timestamp>=-3%20days&type=notify&sort=timestamp&dir=desc&limit=8'
//);
//$dashboard->add(
//    N_('Downtimes Recently Started'),
//    'monitoring/list/eventhistory?timestamp>=-3%20days&type=dt_start&sort=timestamp&dir=desc&limit=8'
//);
//$dashboard->add(
//    N_('Downtimes Recently Ended'),
//    'monitoring/list/eventhistory?timestamp>=-3%20days&type=dt_end&sort=timestamp&dir=desc&limit=8'
//);

/*
 * Stats
 */
//$dashboard = $this->dashboard(N_('Stats'), array('priority' => 99));
//$dashboard->add(
//    N_('Check Stats'),
//    'monitoring/health/stats'
//);
//$dashboard->add(
//    N_('Process Information'),
//    'monitoring/health/info'
//);

/*
 * CSS
 */
$this->provideCssFile('service-grid.less');
$this->provideCssFile('tables.less');
  ```

# Edit Monitoring Page

To remove Custom Variables and Feature Commands , edit this file:
``
/usr/share/icingaweb2/application/modules/monitoring/application/views/scripts/partials/object/detail-content.phtml
``

whith this content:

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

</div>
  ```

# Remove documentation

En el software ir Configuation -> Modules -> doc -> disable

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
