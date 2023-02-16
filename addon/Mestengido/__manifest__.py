
{
    'name': "Mestengido",
    'summary': """
       
       """,

    'description': """
        This modules provides  features - 
      
    """,

    'author': "",
    'website': "",
    'sequence': 108,

    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['hr',  'mail','budget'],
    'data': [
        'data/data.xml',
        'security/mest_group_rules.xml',
        'security/ir.model.access.csv',
        'views/view_menu.xml',
        'views/views.xml',

       
    ],
   
    'images': ['static/description/icon.png'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}