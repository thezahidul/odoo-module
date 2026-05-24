{
    'name': 'Recruiter Approval',
    'version': '19.0.1.0.0',
    'summary': 'Multi-level approval process for Job Posts (1st stage -> 2nd stage -> Final Stage)',
    'sequence': 10,
    'category': 'Human Resources/Payroll',
    'author': 'Zahidul Islam', 
    'license': 'LGPL-3',
    'depends': ['base', 'hr_recruitment','website_hr_recruitment','mail'],
    'data': [
        'security/security.xml',
        'views/hr_job_view.xml',
        'views/hr_applicant_view.xml',
        'reports/offer_letter_report.xml',
        'data/email_template.xml',

    ],
    'assets': {
        'web.report_assets_common': [
            'hr_recruitment_approval/static/src/scss/offer_letter.scss',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': True,
}