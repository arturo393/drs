<?php

namespace Icinga\Module\Director\Web\Table;

use gipfl\IcingaWeb2\Link;
use gipfl\IcingaWeb2\Table\ZfQueryBasedTable;
use ipl\Html\Html;
use Zend_Db_Adapter_Abstract as ZfDbAdapter;
use Zend_Db_Select as ZfDbSelect;

class DatafieldCategoryTable extends ZfQueryBasedTable
{
    protected $searchColumns = array(
        'dfc.varname',
        'dfc.caption',
    );

    public function getColumns()
    {
        return array(
            'id'              => 'dfc.id',
            'category_name'   => 'dfc.category_name',
            'description'     => 'dfc.description',
            'assigned_fields' => 'COUNT(df.id)',
        );
    }

    public function renderRow($row)
    {
        $main = [Link::create(
            $row->category_name,
            'director/datafieldcategory/edit',
            ['name' => $row->category_name]
        )];

        if (strlen($row->description)) {
            $main[] = Html::tag('br');
            $main[] = Html::tag('small', $row->description);
        }
        return $this::tr([
            $this::td($main),
            $this::td($row->assigned_fields)
        ]);
    }

    public function getColumnsToBeRendered()
    {
        return array(
            $this->translate('Category Name'),
            $this->translate('# Used'),
        );
    }

    public function prepareQuery()
    {
        $db = $this->db();
        return $db->select()->from(
            ['dfc' => 'director_datafield_category'],
            $this->getColumns()
        )->joinLeft(
            ['df' => 'director_datafield'],
            'df.category_id = dfc.id',
            []
        )->group('dfc.id')->group('dfc.category_name')->order('category_name ASC');
    }
}
