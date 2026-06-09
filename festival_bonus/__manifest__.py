{
    'name': 'Festival Bonus Management',
    'version': '1.0',
    'depends': ['base', 'hr', 'hr_payroll', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/bonus_config_view.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
}