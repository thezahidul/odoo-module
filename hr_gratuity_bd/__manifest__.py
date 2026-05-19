# -*- coding: utf-8 -*-
{
    'name': 'HR Gratuity - Bangladesh Labor Law',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Payroll',
    'summary': 'Gratuity Management as per Bangladesh Labor Law 2006',
    'description': """
        Bangladesh Labor Law 2006 অনুযায়ী কর্মচারীদের গ্র্যাচুইটি
        ক্যালকুলেশন এবং সেটেলমেন্ট রিপোর্ট।

        Features:
        - আলাদা hr.gratuity মডেল (hr.employee থেকে সম্পূর্ণ আলাদা)
        - BD Labor Law 2006: ৩০ দিন (১-৫ বছর), ৪৫ দিন (৫+ বছর)
        - TDS / Tax calculation with NBR exemption
        - PDF Settlement Report
        - Smart Button on Employee form
        - Demo data: ৪টি বাস্তব উদাহরণ কর্মচারী
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
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
        'report/hr_gratuity_settlement_report.xml',
        'report/hr_gratuity_settlement_template.xml',
    ],
    'demo': [
        'demo/hr_gratuity_demo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
