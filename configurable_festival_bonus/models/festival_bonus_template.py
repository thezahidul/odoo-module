from odoo import models, fields, api


class FestivalBonusTemplate(models.Model):
    _name = "festival.bonus.template"
    _description = "Festival Bonus Template"
    _order = "name"

    name = fields.Char(
        string="Template Name",
        required=True,
        help="e.g. 'Eid Bonus 20%', 'Puja Bonus Standard'",
    )
    active = fields.Boolean(default=True)

    # ── Calculation Rule ──
    bonus_percentage = fields.Float(
        string="Bonus Percentage (%)",
        digits=(5, 2),
        required=True,
    )
    calculation_basis = fields.Selection(
        [
            ("month", "Month Basis (Full Salary %)"),
            ("day", "Day Basis (Pro-rata by Days)"),
        ],
        string="Calculation Basis",
        default="month",
        required=True,
        help="Month: bonus = salary x percentage.\n"
        "Day: bonus = (salary / 30) x eligible_days x percentage.",
    )

    salary_base = fields.Selection(
        [
            ("gross_wage", "Gross Wage"),
            ("basic_wage", "Basic Wage"),
            ("net_wage", "Net Wage"),
        ],
        string="Salary Base",
        default="basic_wage",
        required=True,
        help="Which salary field to use as the base for calculation.",
    )

    min_amount = fields.Monetary(
        string="Minimum Bonus Amount",
        currency_field="currency_id",
        help="If calculated bonus is less than this, this amount applies instead.",
    )
    max_amount = fields.Monetary(
        string="Maximum Bonus Amount",
        currency_field="currency_id",
        help="If calculated bonus exceeds this, it is capped at this amount.",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    # ── Eligibility Rule ──
    # calculation_basis = 'month' হলে min_service_months ব্যবহার হয়
    # calculation_basis = 'day' হলে min_service_days ব্যবহার হয়
    min_service_months = fields.Integer(
        string="Minimum Service (Months)",
        default=6,
        help="Minimum months of service (from joining date to bonus date) "
        "required to be eligible for this bonus. Used when Calculation "
        "Basis is set to Month.",
    )
    min_service_days = fields.Integer(
        string="Minimum Service (Days)",
        default=180,
        help="Minimum days of service (from joining date to bonus date) "
        "required to be eligible for this bonus. Used when Calculation "
        "Basis is set to Day.",
    )

    # ── Eligibility Filter fields (used as default filters when adding employees) ──
    company_id = fields.Many2one("res.company", string="Company")
    department_id = fields.Many2one("hr.department", string="Department")
    job_id = fields.Many2one("hr.job", string="Designation")
    employee_type = fields.Selection(
        [
            ("employee", "Employee"),
            ("student", "Student"),
            ("freelance", "Freelancer"),
        ],
        string="Employee Type",
    )

    note = fields.Text(string="Notes")

    def name_get(self):
        result = []
        for rec in self:
            label = f"{rec.name} ({rec.bonus_percentage}%)"
            result.append((rec.id, label))
        return result
