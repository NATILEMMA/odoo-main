{
  'name':'Gratuity Expense',
  'version': '1.1',
  'description': 'This will handle expesne for gratuity',
  'depends': [
    'hr_gratuity_settlement',
    'hr_expense'
  ],
  'data': [
    'data/gratuity_product.xml',
    'views/hr_gratuity_view_custom.xml',
    'views/hr_expense_view.xml'
  ],
  'category': 'Category',
  'application': False,
  'installable': True,
  'auto_install': False,
  'sequence': 1
}