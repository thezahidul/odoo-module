# -*- coding: utf-8 -*-
{
    'name': 'HR Gratuity Settlement Management',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Automated Gratuity Calculation and Compliance Reporting under Bangladesh Labor Act 2006',
    'author': 'Zahidul Islam',
    'website': 'https://github.com/',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_gratuity_security.xml',
        'views/hr_gratuity_views.xml',
        'views/hr_employee_views.xml',
        'views/hr_gratuity_menu.xml',
        'report/hr_gratuity_settlement_view.xml',
        'report/hr_gratuity_settlement_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}