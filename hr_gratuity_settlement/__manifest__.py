{
    "name": "HR Gratuity Settlement Management",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "summary": "Manage Employee Gratuity Funds and Final Settlements as per Bangladesh Labor Act 2006",
    "author": "Zahidul Islam",
    "depends": ["base", "hr", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_gratuity_view.xml",
        "views/report_action.xml",
        "views/report_template.xml",
    ],
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}
