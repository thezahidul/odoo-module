{
    "name": "Festival Bonus Management",
    "version": "1.0",
    "author": "Zahidul Islam",
    "license": "LGPL-3",
    "category": "Human Resources",
    "summary": "Manage festival bonuses for employees",
    "depends": [
        "base",
        "hr",
        "mail",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/festival_bonus_template_views.xml",  # ← action_festival_bonus_template এখানে define হয়
        "views/festival_bonus_views.xml",  # ← action_festival_bonus এখানে define হয় (menu ছাড়া)
        "views/festival_menus.xml",  # ← সব menu, সবার শেষে
        "views/festival_bonus_wizard_views.xml",
        "views/hr_employee_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "configurable_festival_bonus/static/src/css/style.css",
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
