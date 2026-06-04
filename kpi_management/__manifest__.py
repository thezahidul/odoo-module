{
    'name': 'KPI Management System',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'KPI configuration and employee performance evaluation system.',
    'author': 'Zahidul Islam',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/skill_data.xml',
        'views/kpi_template_views.xml',
        'views/kpi_evaluation_views.xml',
        'views/kpi_skill_library_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}