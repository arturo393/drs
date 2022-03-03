<?php

namespace Icinga\Module\Rs485\Controllers;

use GuzzleHttp\Psr7\ServerRequest;
use Icinga\Module\Rs485\Database;
use Icinga\Application\Config;
use Icinga\Module\Rs485\Forms\SetdruForm;
use Icinga\Web\Controller;
use ipl\Html\Html;
use ipl\Sql\Select;
use ipl\Web\Url;
use ipl\Web\Widget\ButtonLink;
use ipl\Web\Widget\Icon;
use ipl\Web\Widget\Link;


class SetdruController extends Controller
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
            ->from('dru_trama r')
            ->columns(['r.*'])            
            ->orderBy('r.id', SORT_ASC);

        $tableRows = [];

        foreach ($this->getDb()->select($select) as $row) {

            $url = Url::fromPath('rs485/setdru/edit', ['id' => $row->id])->getAbsoluteUrl('&');
            $tableRows[] = Html::tag('tr', ['href' => $url], [
                Html::tag('td', null, $row->name),
                Html::tag('td', null, $row->header),
                Html::tag('td', ['style' => 'background-color: #F2F1EE'], $row->x1),
                Html::tag('td', null, $row->site_number),
                Html::tag('td', null, $row->dru_id),
                Html::tag('td', null, $row->x2),
                Html::tag('td', null, $row->tx_rx1),
                Html::tag('td', null, $row->x3),
                Html::tag('td', null, $row->message_type),
                Html::tag('td', null, $row->tx_rx2),
                Html::tag('td', null, $row->cmd_length),
                Html::tag('td', null, $row->cmd_code),
                Html::tag('td', ['style'=> 'background-color:yellow', 'title'=> $row->cmd_data], substr($row->cmd_data,0,50)),
                Html::tag('td', null, $row->crc),
                Html::tag('td', null, $row->end),
                Html::tag('td', ['class' => 'icon-col'], [
                    new Link(
                        new Icon('edit'),
                        Url::fromPath('rs485/setdru/edit', ['id' => $row->id])
                    )
                ])
            ]);

        }

	if (! empty($tableRows)) {
	    $urlOrder = Url::fromPath('rs485/setdru/list', ['order' => 'name'])->getAbsoluteUrl('&');
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
                                Html::tag('th', null, 'x'),
                                Html::tag('th', null, 'Si'),
                                Html::tag('th', null, 'DRU ID'),
                                Html::tag('th', null, 'x'),
                                Html::tag('th', null, 'Tx/Rx'),
                                Html::tag('th', null, 'x'),
                                Html::tag('th', null, 'M'),
                                Html::tag('th', null, 'Tx/Rx'),
                                Html::tag('th', null, 'Length'),
                                Html::tag('th', null, 'Code'),
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
        $form = (new SetdruForm())
            ->setIniConfig(Config::module('rs485'));

        
        if ($this->_hasParam('id')){
            $id = $this->_getParam('id');
        } else {
            $id = 0;
        }
        $select = (new Select())
        ->from('dru_trama r')
        ->columns(['r.*'])
        ->where(['r.id = ?' => $id]);

        $row  = $this->getDb()->select($select)->fetch();
        if ($row) {
            $this->view->assign('descripcion', $row->name);
            $trama = $this->armaTrama($row);
            $this->view->assign('trama', $trama);
			  
	    $values = [
		        'id' => $row->id,
		        'dru_cmdlength'  => $row->cmd_length,
			'dru_cmdcode'  => $row->cmd_code,
			'dru_cmddata'  => $row->cmd_data,
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
	$druCmdLength = -1;    
	$druCmdCode = -1; 
    $druCmdData = -1;
    $user_remote = -1;
    $password_remote = -1;
    $host_remote = -1;	
       // Check if user has submitted the form
       if($this->getRequest()->isPost()) {

	    if ($this->_hasParam('id')){
		    $id = $this->_getParam('id');
	    }

	    if ($this->_hasParam('dru_cmdlength')){
                $druCmdLength = $this->_getParam('dru_cmdlength');
	    }

	    if ($this->_hasParam('dru_cmdcode')){
                $druCmdCode = $this->_getParam('dru_cmdcode');
	    } 

	    if ($this->_hasParam('dru_cmddata')){
                $druCmdData = $this->_getParam('dru_cmddata');
        }

        if ($this->_hasParam('user_remote')){
            $user_remote = $this->_getParam('user_remote');
        }
    
        if ($this->_hasParam('password_remote')){
            $password_remote = $this->_getParam('password_remote');
        }
        
        if ($this->_hasParam('host_remote')){
            $host_remote = $this->_getParam('host_remote');
        }    
       }

	$select = (new Select())
        ->from('dru_trama r')
        ->columns(['r.*'])
        ->where(['r.id = ?' => $id]);

        $row  = $this->getDb()->select($select)->fetch();
	if ($row) {
		$druId = $row->dru_id;

        }
	$paramFijos = '--port /dev/ttyUSB1 --action set --device dru ';
	$paramVariables = "--druId {$druId} --cmdBodyLenght {$druCmdLength} --cmdNumber {$druCmdCode} --cmdData {$druCmdData}";
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
	   $trama = $data->header . $data->x1 . $data->site_number . $data->dru_id . $data->x2 . $data->tx_rx1 . $data->x3 . $data->message_type . $data->tx_rx2 . $data->cmd_length . $data->cmd_code . $data->cmd_data . $data->crc . $data->end;
	   return $trama; 
    }


}

