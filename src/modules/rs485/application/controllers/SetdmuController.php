<?php

namespace Icinga\Module\Rs485\Controllers;

use GuzzleHttp\Psr7\ServerRequest;
use Icinga\Module\Rs485\Database;
use Icinga\Application\Config;
use Icinga\Module\Rs485\Forms\SetdmuForm;
use Icinga\Web\Controller;
use ipl\Html\Html;
use ipl\Sql\Select;
use ipl\Web\Url;
use ipl\Web\Widget\ButtonLink;
use ipl\Web\Widget\Icon;
use ipl\Web\Widget\Link;


class SetdmuController extends Controller
{
    use Database;

    public function init()
    {
        $this->assertPermission('config/modules');
        parent::init();
    }

    public function listAction()
    {
        $select = (new Select())
            ->from('rs485_dmu_trama r')
            ->columns(['r.*'])            
            ->orderBy('r.id', SORT_ASC);

        $tableRows = [];

        foreach ($this->getDb()->select($select) as $row) {

            $url = Url::fromPath('rs485/setdmu/edit', ['id' => $row->id])->getAbsoluteUrl('&');
            $tableRows[] = Html::tag('tr', ['href' => $url], [
                Html::tag('td', null, $row->name),
                Html::tag('td', null, $row->header),
                Html::tag('td', ['style' => 'background-color: #F2F1EE'], $row->dmu_device1),
                Html::tag('td', null, $row->dmu_device2),
                Html::tag('td', null, $row->data_type),
                Html::tag('td', null, $row->cmd_number),
                Html::tag('td', null, $row->response_flag),
                Html::tag('td', null, $row->cmd_body_lenght),
                Html::tag('td', ['style'=> 'background-color:yellow', 'title'=> $row->cmd_data], substr($row->cmd_data,0,50)),
                Html::tag('td', null, $row->crc),
                Html::tag('td', null, $row->end),
                Html::tag('td', ['class' => 'icon-col'], [
                    new Link(
                        new Icon('edit'),
                        Url::fromPath('rs485/setdmu/edit', ['id' => $row->id])
                    )
                ])
            ]);

        }

	if (! empty($tableRows)) {
	    $urlOrder = Url::fromPath('rs485/setdmu/list', ['order' => 'name'])->getAbsoluteUrl('&');
            $table = Html::tag(
                'table',
                ['class' => 'common-table table-row-selectable', 'data-base-target' => '_next'],
                [
                    Html::tag(
                        'thead',
                        null,
                        Html::tag(
                            'tr',
                            null,
                            [
                                Html::tag('th', null, 'Comando'),
                                Html::tag('th', null, 'H'),
                                Html::tag('th', null, 'd1'),
                                Html::tag('th', null, 'd2'),
                                Html::tag('th', null, 'DT'),
                                Html::tag('th', null, 'Cmd N'),
                                Html::tag('th', null, 'f'),
                                Html::tag('th', null, 'lengh'),
                                Html::tag('th', null, 'Data'),
                                Html::tag('th', null, 'Data'),
                                Html::tag('th', null, 'CRC'),
                                Html::tag('th', null, 'End'),
                                Html::tag('th')
                            ]
                        )
                    ),
                    Html::tag('tbody', null, $tableRows)
                ]
            );

            $this->view->assign('table_view', $table);
        } else {
            $this->view->assign('table_view', Html::tag('p', null, 'No reports created yet.'));
        }
    }



    public function editAction()
    {
        $form = (new SetdmuForm())
            ->setIniConfig(Config::module('rs485'));

        
        if ($this->_hasParam('id')){
            $id = $this->_getParam('id');
        } else {
            $id = 0;
        }
        $select = (new Select())
        ->from('rs485_dmu_trama r')
        ->columns(['r.*'])
        ->where(['r.id = ?' => $id]);

        $row  = $this->getDb()->select($select)->fetch();
        if ($row) {
            $this->view->assign('descripcion', $row->name);
	    $trama = $this->armaTrama($row);
            $this->view->assign('trama', $trama);
			  
	    $values = [
		        'id' => $row->id,
		        'dmu_cmdlength'  => $row->cmd_body_lenght,
			'dmu_cmddata'  => $row->cmd_data,
            // TODO(el): Must cast to string here because ipl/html does not
            //           support integer return values for attribute callbacks
            ];

            $form->populate($values);        
        }


        $form->handleRequest();

        $this->view->form = $form;

        $this->view->assign('id', $id);
       }


    public function saveAction()
    {
	$id = 0;
	$dmuCmdLength = -1;    
    $dmuCmdData = -1;
    $user_remote = -1;    
    $host_remote = -1;	
       // Check if user has submitted the form
       if($this->getRequest()->isPost()) {

	    if ($this->_hasParam('id')){
		    $id = $this->_getParam('id');
	    }

	    if ($this->_hasParam('dmu_cmdlength')){
                $dmuCmdLength = $this->_getParam('dmu_cmdlength');
	    }


	    if ($this->_hasParam('dmu_cmddata')){
                $dmuCmdData = $this->_getParam('dmu_cmddata');
            }
        
        if ($this->_hasParam('user_remote')){
            $user_remote = $this->_getParam('user_remote');
        }
            
        if ($this->_hasParam('host_remote')){
            $host_remote = $this->_getParam('host_remote');
        }
       }

	$select = (new Select())
        ->from('rs485_dmu_trama r')
        ->columns(['r.*'])
        ->where(['r.id = ?' => $id]);

        $row  = $this->getDb()->select($select)->fetch();
	if ($row) {
		$dmuCmdCode = $row->cmd_number;
		$dmuDevice1 = $row->dmu_device1;
		$dmuDevice2 = $row->dmu_device2;

        }
        $paramFijos = '--port /dev/ttyUSB0 --action set --device dmu ';
        $paramVariables = "--dmuDevice1 {$dmuDevice1} --dmuDevice2 {$dmuDevice2} --cmdBodyLenght {$dmuCmdLength} --cmdNumber {$dmuCmdCode} --cmdData {$dmuCmdData}";
        $comando = "/usr/lib/monitoring-plugins/check_rs485.py ";
        $ssh = "sudo -u sigmadev ssh {$user_remote}@{$host_remote} ";
        $ejecutar =  $ssh . $comando . $paramFijos . $paramVariables;
        $salida = system($ejecutar . " 2>&1");
        usleep(500000);
        //echo "salida: <pre>". $salida ."</pre>";
        $this->view->assign('salida', $salida);
        $this->view->assign('cmd', $ejecutar);	
    }

    private function armaTrama($data)
    {
	   $trama = $data->header . $data->dmu_device1 . $data->dmu_device2 . $data->data_type . $data->cmd_number . $data->response_flag . $data->cmd_body_lenght . $data->cmd_data . $data->crc . $data->end;
	   return $trama; 
    }


}

