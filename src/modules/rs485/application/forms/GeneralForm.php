<?php
// Icinga Rs485 | (c) 2019 Icinga GmbH | GPLv2

namespace Icinga\Module\Rs485\Forms;

use Icinga\Forms\ConfigForm;
use Icinga\Module\Rs485\Database;
use ipl\Sql\Select;

class GeneralForm extends ConfigForm
{
    use Database;

    public function init()
    {
        $this->setName('form_general');
            $this->setSubmitLabel($this->translate('Enviar Trama'));
        $this->setAction('rs485/general/edit');
    }

    public function createElements(array $formData)
    {
        $listHost = $this->cargarHost();


        $this->addElement(
              'select',
              'host_remote',
              array(
                  'label' => $this->translate('Host'),
                  'multiOptions' => $listHost,
                  'required' => true,
                  // 'autosubmit' acts like an AJAX-Request
                  //'class' => 'autosubmit'
              )
          );

        $this->addElement('text', 'user_remote', [
            'label'       => $this->translate('Usuario'),
            'placeholder' => 'user',
            'required' => true,
        ]);

        $this->addElement(
            'select',
            'action',
            array(
                'label' => $this->translate('Action'),
         'multiOptions' => [ 'set' => 'Set' ],
             'required' => true,
                // 'autosubmit' acts like an AJAX-Request
                //'class' => 'autosubmit'
           )
        );

        $this->addElement(
            'select',
            'device',
            array(
                'label' => $this->translate('Device'),
         'multiOptions' => [
            ''    => '(Select device)',
            'dmu' => 'DMU',
            'dru' => 'DRU'
        ],
           'required' => true,
                // 'autosubmit' acts like an AJAX-Request
            'class' => 'autosubmit'
           )
        );

        if (isset($formData['device']) && $formData['device'] != '') {
            $device = $formData['device'];
            if ($device === "dmu") {
                $listTrama = $this->tramasDMU();
                $port = ['/dev/ttyS0' => '/dev/ttyS0'];
                $labelCmdLength = 'CMD body Length';
                $labelCmdCode = 'CMD Number';
                $labelCmdData = 'CMD Data';
            }else {
                $listTrama = $this->tramasDRU();
                $port = ['' => '(select Port)',
                        '/dev/ttyS1' => '/dev/ttyS1',
                        '/dev/ttyS2' => '/dev/ttyS2',
                        '/dev/ttyS4' => '/dev/ttyS3',
                        '/dev/ttyS4' => '/dev/ttyS4',
                        ];
                        $labelCmdLength = 'CMD Length';
                        $labelCmdCode = 'CMD Code';
                        $labelCmdData = 'CMD Data';
            }
            $this->addElement(
                'select',
                'port',
                array(
                    'label' => $this->translate('Port'),
             'multiOptions' => $port,
            'required' => true,
                    // 'autosubmit' acts like an AJAX-Request
                    //'class' => 'autosubmit'
            )
            );

            $this->addElement(
                'select',
                'trama',
                array(
                    'label' => $this->translate('Trama'),
             'multiOptions' => $listTrama,
            'required' => true,
                    // 'autosubmit' acts like an AJAX-Request
                    //'class' => 'autosubmit'
            )
            );

            $trama = isset($formData['trama']) ? $formData['trama'] : '';
            $this->addElement(
                'select',
                'trama',
                array(
                    'label' => $this->translate('Trama'),
                    'value' => $trama,
             'multiOptions' => $listTrama,
            'required' => true,
                    // 'autosubmit' acts like an AJAX-Request
                    //'class' => 'autosubmit'
            )
            );


        $this->addElement('text', 'cmdlength', [
            'label'       => $this->translate("{$labelCmdLength}"),
            'placeholder' => '04',
            'required' => true,
        ]);

        $this->addElement('text', 'cmdcode', [
            'label'       => $this->translate( "{$labelCmdCode}"),
            'placeholder' => 'EF',
            'required' => true,
        ]);

        $this->addElement('text', 'cmddata', [
            'label'       => $this->translate($labelCmdData),
            'placeholder' => '00FF01',
            'required' => true,
            ]);
       }


            $this->addElement('hidden', 'id', null);
    }

    private function cargarHost(){
            $select = (new Select())
            ->from('icinga_host r')
            ->columns(['r.*'])
            ->where(['r.object_type = ?' => 'object'])
            ->orderBy('r.object_name', SORT_ASC);
          $list[''] = '(select Host)';
         foreach ($this->getDb()->select($select) as $row) {
                    $list[$row->address] = "{$row->object_name} - {$row->address}";
         }
        return $list;
    }

    private function tramasDMU(){
        $select = (new Select())
            ->from('rs485_dmu_trama r')
            ->columns(['r.*'])
            ->orderBy('r.name', SORT_ASC);
        $list[''] = '(select Trama)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;
        }
        return $list;
    }

    private function tramasDRU(){
        $select = (new Select())
            ->from('rs485_dru_trama r')
            ->columns(['r.*'])
            ->orderBy('r.name', SORT_ASC);

        $list[''] = '(select Trama)';

        foreach ($this->getDb()->select($select) as $row) {
            $list[$row->id] = $row->name;
        }
        return $list;

    }
}
