{
    'name': 'Festival Bonus Management',
    'version': '1.0',
    'author': 'Your Name',
    'license': 'LGPL-3',
    'category': 'Human Resources',
    'summary': 'Manage festival bonuses for employees',
    'depends': [
        'base',
        'hr',
        'mail',
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/festival_bonus_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}