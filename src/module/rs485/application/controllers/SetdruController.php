<?php

namespace Icinga\Module\Rs485\Controllers;

use GuzzleHttp\Psr7\ServerRequest;
use Icinga\Application\Config;
use Icinga\Module\Rs485\Forms\SetdruForm;
use Icinga\Web\Controller;
use ipl\Html\Html;
use ipl\Web\Url;
use ipl\Web\Widget\ButtonLink;
use ipl\Web\Widget\Icon;
use ipl\Web\Widget\Link;


class SetdruController extends Controller
{
    private $arraySet = array(
       array('id' => 1, 
             'name' => 'Site Number (DMU ID)', 
             'header' => '7E', 
             'x1' => '01 01' ,
             'site_number' => '00 00 00 00',
             'dru_id' => '11' ,
             'x2' => '01 00' ,
             'tx_rx1' => '80' ,
             'x3' => '01' ,
             'message_type' => '03' ,
             'tx_rx2' => 'FF' ,
             'cmd_length' => '07' ,
             'cmd_code' => '01 01' ,
             'cmd_data' => '00 00 00 00' ,
             'crc' => 'DB 30' ,
             'end' => '7E' 
             ) ,

       array('id' => 2, 
             'name' => 'Site Subnumber (DRU ID)', 
             'header' => '7E', 
             'x1' => '00 00', 
             'site_number' => '00 00 00 00',
             'dru_id' => '11' ,
             'x2' => '01 00' ,
             'tx_rx1' => '80' ,
             'x3' => '01' ,
             'message_type' => '03' ,
             'tx_rx2' => 'FF' ,
             'cmd_length' => '04' ,
             'cmd_code' => '02 01' ,
             'cmd_data' => '11' ,
             'crc' => 'B7 E0' ,
             'end' => '7E' 
             )  
        );
    
    public function init()
    {
        $this->assertPermission('config/modules');
        parent::init();
    }

    public function listAction()
    {
        $tableRows = [];
        foreach ($this->arraySet as $row) {
        $url = Url::fromPath('rs485/setdru/dru', ['id' => $row['id']])->getAbsoluteUrl('&');
            //$trama = $this->obtenerTrama($row);
            //$trama = $row['header'] . $row['x1'];
            $tableRows[] = Html::tag('tr', ['href' => $url], [
                Html::tag('td', null, $row['name']),
                //Html::tag('td', null, $trama),
                Html::tag('td', null, $row['header']),
                Html::tag('td', null, $row['x1']),
                Html::tag('td', null, $row['site_number']),
                Html::tag('td', null, $row['dru_id']),
                Html::tag('td', null, $row['x2']),
                Html::tag('td', null, $row['tx_rx1']),
                Html::tag('td', null, $row['x3']),
                Html::tag('td', null, $row['message_type']),
                Html::tag('td', null, $row['tx_rx2']),
                Html::tag('td', null, $row['cmd_length']),
                Html::tag('td', null, $row['cmd_code']),
                Html::tag('td', null, $row['cmd_data']),
                Html::tag('td', null, $row['crc']),
                Html::tag('td', null, $row['end']),

                Html::tag('td', ['class' => 'icon-col'], [
                    new Link(
                        new Icon('edit'),
                        Url::fromPath('rs485/setdru/dru', ['id' => $row['id']])
                    )
                ])
            ]);
        }

        if (! empty($tableRows)) {
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

            //$this->addContent($table);
            $this->view->assign('table_view', $table);
        } else {
            $this->view->assign('table_view', Html::tag('p', null, 'No reports created yet.'));
           // $this->addContent(Html::tag('p', null, 'No reports created yet.'));
        }
    }



    public function druAction()
    {
        $form = (new SetdruForm())
            ->setIniConfig(Config::module('rs485'));

        $form->handleRequest();

        //$this->view->tabs = $this->Module()->getConfigTabs()->activate('form');
        $this->view->form = $form;



            $this->view->application = 'Icinga Web rdu';
        $this->view->moreData = array(
        'Work'   => 'done',
        'Result' => 'fantastic'
        );

        echo "Paso x aca druAction";
    }

    public function saveAction()
    {
            // Check if user has submitted the form
       if($this->getRequest()->isPost()) {

          // Retrieve form data from POST variables
            //$data = $this->params()->fromPost();
            // // Get all route parameters at once as an array.
            //$data = $this->params()->fromRoute();
            if ($this->_hasParam('dru_cmdcode')){
                $postId = $this->_getParam('dru_cmdcode');
            } else {
                $postId = 1;
            }

          // ... Do something with the data ...
          //var_dump($postId);
          }
            echo "Llego a guardar la informacion";
//           $postId  = $data['dru_cmdcode'];
            //$postId = $this->params()->fromPost('dru_cmdcode');
            $salida = shell_exec("cd /usr/lib/monitoring-plugins/ && ./check_dummy {$postId}" );
           echo "<pre>$salida</pre>";
           $this->view->assign('dru_cmdcode', $salida);//assign here
    }
    
    private function obtenerTrama($row){
        $trama = $row['header']. ' ' . 
                 $row['x1'] . ' ' .
                 $row['site_number']  . ' ' .     
                 $row['dru_id']  . ' ' .       
                 $row['x2']  . ' ' .       
                 $row['x3']  . ' ' .       
                 $row['message_type']  . ' ' .               
                 $row['tx_rx2']  . ' ' .       
                 $row['cmd_length']  . ' ' .       
                 $row['cmd_code']  . ' ' .       
                 $row['crc']  . ' ' .      
                 $row['end'];     

                 

        /*Html::tag('td', null, ),
        Html::tag('td', null, ),
        Html::tag('td', null, ),
        Html::tag('td', null, $row['dru_id']),
        Html::tag('td', null, $row['x2']),
        Html::tag('td', null, $row['tx_rx1']),
        Html::tag('td', null, $row['x3']),
        Html::tag('td', null, $row['message_type']),
        Html::tag('td', null, $row['tx_rx2']),
        Html::tag('td', null, $row['cmd_length']),
        Html::tag('td', null, $row['cmd_code']),
        Html::tag('td', null, $row['cmd_data']),
        Html::tag('td', null, $row['crc']),
        Html::tag('td', null, $row['end']),*/
        return $trama;
    }

    

}

