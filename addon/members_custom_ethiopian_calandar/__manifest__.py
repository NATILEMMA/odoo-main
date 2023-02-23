
{
    "name": "Ethiopian Calendar members custom",
    "summary": "Ethiopian Calenda members custom"
    "company",
    "version": "13.0.1",
    "author": "mes",
    "website": " ",
    "category": "",
    "depends": ["contacts","base","calendar","members_custom"],
    "license": "LGPL-3",
    "data": [
        'security/ir.model.access.csv',

        "views/assets.xml",
        "views/view.xml",
        "views/inherit_view.xml",
        "views/complaint_category_view.xml",
        "views/main_office_view.xml" 
    ],
      'application': True,
  'qweb': [
        'static/ethiopian_datepicker.xml'
    ],
  'installable': True,
  'auto_install': False,
  'sequence': 1001

}
