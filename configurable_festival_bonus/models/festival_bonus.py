from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FestivalBonusConfig(models.Model):
    _name = "festival.bonus.config"
    _description = "Festival Bonus Configuration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "bonus_date desc"

    name = fields.Char(string="Festival Name", required=True, tracking=True)

    bonus_date = fields.Date(
        string="Bonus Applicable Date",
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help="The reference date used to calculate each employee's service "
        "duration (joining date -> this date) for eligibility and "
        "pro-rata bonus calculation.",
    )

    # ── Template link ──
    template_id = fields.Many2one(
        "festival.bonus.template",
        string="Bonus Template",
        required=True,
        tracking=True,
        help="Select a template to auto-fill the calculation rule below.",
    )

    # ── Rule fields (copied from template on selection, editable afterwards) ──
    salary_base = fields.Selection(
        [
            ("gross_wage", "Gross Wage"),
            ("basic_wage", "Basic Wage"),
            ("net_wage", "Net Wage"),
        ],
        string="Salary Base",
        required=True,
        default="basic_wage",
        tracking=True,
    )

    bonus_percentage = fields.Float(
        string="Bonus Percentage (%)",
        digits=(5, 2),
        tracking=True,
        help="Used when 'Use Designation-wise Bonus %' is OFF.",
    )
    use_designation_rates = fields.Boolean(
        string="Use Designation-wise Bonus %",
        tracking=True,
        help="If enabled, bonus percentage is determined per employee's "
        "Designation. Employees whose designation is not listed will "
        "NOT be eligible (0 bonus).",
    )
    designation_rate_ids = fields.One2many(
        "festival.bonus.designation.rate",
        "config_id",
        string="Designation-wise Rates",
    )
    calculation_basis = fields.Selection(
        [
            ("month", "Month Basis (Full Salary %)"),
            ("day", "Day Basis (Pro-rata)"),
        ],
        string="Calculation Basis",
        default="month",
        required=True,
        tracking=True,
    )

    min_amount = fields.Monetary(
        string="Minimum Bonus Amount", currency_field="currency_id"
    )
    max_amount = fields.Monetary(
        string="Maximum Bonus Amount", currency_field="currency_id"
    )

    min_service_months = fields.Integer(
        string="Minimum Service (Months)",
        default=6,
        tracking=True,
        help="Used for eligibility check when Calculation Basis = Month.",
    )
    min_service_days = fields.Integer(
        string="Minimum Service (Days)",
        default=180,
        tracking=True,
        help="Used for eligibility check when Calculation Basis = Day.",
    )

    # ── Filter fields (copied from template, used as wizard defaults) ──
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

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
        ],
        default="draft",
        tracking=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one("res.currency", related="company_id.currency_id")

    bonus_line_ids = fields.One2many(
        "festival.bonus.line",
        "bonus_id",
        string="Bonus Lines",
    )
    total_bonus = fields.Monetary(
        string="Total Bonus",
        currency_field="currency_id",
        compute="_compute_total_bonus",
        store=True,
    )

    @api.depends("bonus_line_ids.bonus_amount")
    def _compute_total_bonus(self):
        for rec in self:
            rec.total_bonus = sum(rec.bonus_line_ids.mapped("bonus_amount"))

    # ── Template selected → auto-fill all rule fields ──
    @api.onchange("template_id")
    def _onchange_template_id(self):
        if not self.template_id:
            return
        t = self.template_id
        self.salary_base = t.salary_base
        self.bonus_percentage = t.bonus_percentage
        self.calculation_basis = t.calculation_basis
        self.min_amount = t.min_amount
        self.max_amount = t.max_amount
        self.min_service_months = t.min_service_months
        self.min_service_days = t.min_service_days
        self.use_designation_rates = t.use_designation_rates

        # Designation-wise rate rows কপি করো (নতুন, independent রেকর্ড হিসেবে)
        rate_commands = [(5, 0, 0)]  # প্রথমে existing সব clear করো
        for rate in t.designation_rate_ids:
            rate_commands.append(
                (
                    0,
                    0,
                    {
                        "job_id": rate.job_id.id,
                        "bonus_percentage": rate.bonus_percentage,
                        "sequence": rate.sequence,
                    },
                )
            )
        self.designation_rate_ids = rate_commands

        self.department_id = t.department_id
        self.job_id = t.job_id
        self.employee_type = t.employee_type
        if t.company_id:
            self.company_id = t.company_id

        # Template change হলে existing employee lines ও recalculate করো
        self._recalculate_all_lines()

    # ── Any rule field changed manually → recalculate existing lines ──
    @api.onchange(
        "salary_base",
        "bonus_percentage",
        "calculation_basis",
        "min_amount",
        "max_amount",
        "min_service_months",
        "min_service_days",
        "bonus_date",
        "use_designation_rates",
        "designation_rate_ids",
    )
    def _onchange_rule_fields(self):
        self._recalculate_all_lines()

    def _recalculate_all_lines(self):
        if not self.bonus_line_ids:
            return
        for line in self.bonus_line_ids:
            if not line.employee_id:
                continue
            line.salary_base_amount = line._get_salary_from_payslip(
                line.employee_id,
                self.salary_base,
            )
            line._compute_eligibility()
            line._compute_bonus_amount()

    def get_percentage_for_employee(self, employee):
        """
        Employee-er jonno applicable bonus percentage বের করে।
        use_designation_rates ON হলে -> employee.job_id দিয়ে designation_rate_ids
        এ match খোঁজে; match না পেলে 0.0 (not eligible)।
        OFF হলে -> single bonus_percentage সবার জন্য প্রযোজ্য।
        """
        self.ensure_one()
        if not self.use_designation_rates:
            return self.bonus_percentage or 0.0

        if not employee.job_id:
            return 0.0

        rate = self.designation_rate_ids.filtered(lambda r: r.job_id == employee.job_id)
        if rate:
            return rate[0].bonus_percentage
        return 0.0

    def action_confirm_bonus(self):
        self.ensure_one()
        if not self.bonus_line_ids:
            raise UserError(_("Please add employees before confirming."))
        self.state = "confirmed"

    def action_reset_draft(self):
        self.ensure_one()
        self.state = "draft"

    def action_open_bulk_add_wizard(self):
        self.ensure_one()
        return {
            "name": _("Add Employees"),
            "type": "ir.actions.act_window",
            "res_model": "festival.bonus.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_bonus_id": self.id,
                "default_department_id": self.department_id.id,
                "default_job_id": self.job_id.id,
                "default_employee_type": self.employee_type,
                "default_company_id": self.company_id.id,
            },
        }
