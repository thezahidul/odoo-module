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

    template_id = fields.Many2one(
        "festival.bonus.template",
        string="Bonus Template",
        required=True,
        tracking=True,
        help="Select a template to auto-fill the calculation rule below.",
    )

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
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
        tracking=True,
    )
    department_id = fields.Many2one("hr.department", string="Department")
    job_id = fields.Many2one("hr.job", string="Designation")
    employee_type = fields.Selection(
        selection="_get_employee_types",
        string="Employee Type",
    )

    @api.model
    def _get_employee_types(self):
        selection = self.env["hr.employee"]._fields["employee_type"].selection
        if callable(selection):
            return selection(self.env["hr.employee"])
        return selection

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
        ],
        default="draft",
        tracking=True,
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

    # ── Accounting fields ──
    expense_account_id = fields.Many2one(
        "account.account",
        string="Expense Account",
        domain="[('account_type', '=', 'expense')]",
    )
    payable_account_id = fields.Many2one(
        "account.account",
        string="Payable Account",
        domain="[('account_type', '=', 'liability_current')]",
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Journal",
        domain="[('type', '=', 'general')]",
    )
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True)

    # ── Compute ──
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
        self.expense_account_id = t.expense_account_id
        self.payable_account_id = t.payable_account_id
        self.journal_id = t.journal_id

        # Designation-wise rate rows copy
        rate_commands = [(5, 0, 0)]
        for rate in t.designation_rate_ids:
            rate_commands.append(
                (
                    0,
                    0,
                    {
                        "company_id": rate.company_id.id,
                        "department_id": rate.department_id.id,
                        "job_id": rate.job_id.id,
                        "bonus_percentage": rate.bonus_percentage,
                        "sequence": rate.sequence,
                    },
                )
            )
        self.designation_rate_ids = rate_commands

        # Filter fields copy
        self.department_id = t.department_id
        self.job_id = t.job_id
        self.employee_type = t.employee_type
        if t.company_id:
            self.company_id = t.company_id

        self._recalculate_all_lines()

    # ── Any rule field changed manually → recalculate lines ──
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
        """Find the applicable bonus % according to the employee's job_id"""
        self.ensure_one()
        if not self.use_designation_rates:
            return self.bonus_percentage or 0.0
        if not employee.job_id:
            return 0.0
        rate = self.designation_rate_ids.filtered(lambda r: r.job_id == employee.job_id)
        return rate[0].bonus_percentage if rate else 0.0

    def action_confirm_bonus(self):
        self.ensure_one()

        # 1. Duplicate employee remove
        seen = set()
        to_unlink = self.env["festival.bonus.line"]
        for line in self.bonus_line_ids:
            if line.employee_id.id in seen:
                to_unlink |= line
            else:
                seen.add(line.employee_id.id)
        if to_unlink:
            to_unlink.unlink()

        # 2. Validation
        if not self.bonus_line_ids:
            raise UserError(_("Please add employees before confirming."))
        if not self.expense_account_id or not self.payable_account_id:
            raise UserError(
                _("Please configure the Expense and Payable accounts first.")
            )
        if not self.journal_id:
            raise UserError(_("Please select a Journal before confirming."))
        if self.total_bonus <= 0:
            raise UserError(_("Total bonus amount must be greater than zero."))

        # 3. Journal lines createtion
        move_lines = []
        for line in self.bonus_line_ids:
            if not line.bonus_amount:
                continue
            move_lines.append(
                (
                    0,
                    0,
                    {
                        "name": f"{self.name} - {line.employee_id.name}",
                        "partner_id": line.employee_id.work_contact_id.id,
                        "account_id": self.expense_account_id.id,
                        "debit": line.bonus_amount,
                        "credit": 0.0,
                    },
                )
            )

        move_lines.append(
            (
                0,
                0,
                {
                    "name": f"Total Festival Bonus: {self.name}",
                    "account_id": self.payable_account_id.id,
                    "debit": 0.0,
                    "credit": self.total_bonus,
                },
            )
        )

        # 4. Journal entry creation
        move = self.env["account.move"].create(
            {
                "journal_id": self.journal_id.id,
                "date": fields.Date.today(),
                "ref": _("Festival Bonus: ") + self.name,
                "state": "draft",
                "line_ids": move_lines,
            }
        )
        self.move_id = move.id
        self.state = "confirmed"

    def action_reset_draft(self):
        self.ensure_one()
        if self.move_id:
            if self.move_id.state == "posted":
                raise UserError(_("Cannot reset: journal entry is already posted!"))
            if self.move_id.state != "cancel":
                raise UserError(
                    _("Cannot reset: please cancel the journal entry first!")
                )
            self.move_id.unlink()
            self.move_id = False
        self.state = "draft"

    def action_view_journal_entry(self):
        self.ensure_one()
        return {
            "name": _("Journal Entry"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.move_id.id,
        }

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
