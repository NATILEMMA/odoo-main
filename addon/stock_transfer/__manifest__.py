# ++++++++++++++++++++++++++++++++++++++++++++
{
    'name': 'Stock Transfer',
    'version': '1.1',
    'summary': 'Stock Transfer Request',
    'description': """ 
            """,
    'depends': ['sprogroup_purchase_request'],
    'category': 'Extra',
    'sequence': 1,
    'data': [
        'views/menus.xml',
        'security/ir.model.access.csv',
        'sequences/sequences.xml'
    ],
    'test': [
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'auto_install': True,
    'application': True
}
