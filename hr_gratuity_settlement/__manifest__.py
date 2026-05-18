{
    "name": "HR Gratuity Settlement",
    "version": "1.0",
    "category": "Human Resources",
    "summary": "Gratuity Settlement Management based on Bangladesh Labour Law",
    "sequence": 20,
    "depends": ["base", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/gratuity_settlement_view.xml",
        "views/gratuity_settlement_report_action.xml",
    ],
    "author": "Zahidul Islam",
    "license": "LGPL-3",
    "installable": True,
    "application": True,
    "auto_install": False,
}
