{
    'name': 'Recruiter Approval',
    'version': '19.0.1.0.0',
    'summary': 'Multi-level approval process for Job Posts (1st stage -> 2nd stage -> Final Stage)',
    'sequence': 10,
    'description': """
        This module adds a custom status flow for hr.job:
        1. Draft
        2. 1st stage 
        3. 2nd stage
        4. Final Stage
    """,
    'category': 'Education',
    'author': 'Zahidul Islam', 
    'license': 'LGPL-3',
    'depends': ['base', 'hr_recruitment','website_hr_recruitment','mail'],
    'data': [
        'security/security.xml',
        'views/hr_job_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}