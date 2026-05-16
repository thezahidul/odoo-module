{
    "name": "HR Gratuity Fund (GF)",
    "version": "1.0",
    "category": "Human Resources",
    "summary": "Automated Gratuity Calculation based on Bangladesh Labour Law",
    "sequence": 20,
    "depends": ["base", "hr"],
    "data": [
        'views/report_action.xml',
        'views/report_template.xml',
        "views/hr_employee_view.xml",
        
    ],
    "author": "Zahidul Islam",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "auto_install": False,
}
