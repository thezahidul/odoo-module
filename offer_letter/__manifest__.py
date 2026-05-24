{
    'name': 'Offer Letter Management',
    'version': '1.0',
    'depends': ['hr_recruitment', 'mail'],
    'data': [
        'views/hr_applicant_view.xml',
        'reports/offer_letter_report.xml',
        'data/email_template.xml',
    ],
    'assets': {
        'web.report_assets_common': [
            'offer_letter/static/src/scss/offer_letter.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False
}