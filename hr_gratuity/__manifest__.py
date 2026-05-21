# -*- coding: utf-8 -*-
{
    'name': 'Custom HR Gratuity',
    'summary': 'Dynamic Multi-Tier Gratuity Configuration, Tenure Tracking, and Final Settlement Pipeline',
    'category': 'Human Resources/Payroll',
    'version': '19.0.1.0.0',
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
        'report/hr_gratuity_settlement_template.xml',
        'report/hr_gratuity_settlement_view.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'hr_gratuity/static/src/css/gratuity_report.css',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}