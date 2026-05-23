{
    'name': 'Offer Letter Management',
    'version': '1.0',
    'depends': ['hr_recruitment', 'mail'],
    'data': [
        'views/hr_applicant_view.xml',
        'reports/offer_letter_report.xml',
        'data/email_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}