<?php
$section = $this->menuSection(
    N_('Network Maps'),
)->setUrl('network_maps/module/network')->setIcon('sitemap'
)->setRenderer(array(
    'SummaryNavigationItemRenderer',
    'state' => 'critical'
));

$section->add(N_('Settings'))
    ->setUrl('network_maps/module/settings');

$this->provideJsFile('fullscreenManager.js');
$this->provideJsFile('gridManager.js');
$this->provideJsFile('graphManager.js');
$this->provideJsFile('vendor/vis.min.js');
$this->provideJsFile('graphManager.js');
$this->provideJsFile('requestsManager.js');
$this->provideJsFile('kickstartManager.js');
$this->provideJsFile('errorManager.js');
$this->provideJsFile('settingsManager.js');


?>