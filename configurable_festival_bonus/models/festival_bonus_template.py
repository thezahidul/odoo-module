from odoo import models, fields, api


class FestivalBonusTemplate(models.Model):
    _name = "festival.bonus.template"
    _description = "Festival Bonus Template"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(
        string="Template Name",
        required=True,
        help="e.g. 'Eid Bonus 20%', 'Puja Bonus Standard'",
    )
    active = fields.Boolean(default=True)

    # Calculation Rule
    use_designation_rates = fields.Boolean(
        string="Use Designation-wise Bonus %",
        default=False,
        help="If enabled, bonus percentage is determined per employee's "
        "Designation using the table below. Employees whose designation "
        "is not listed will NOT be eligible (0 bonus). "
        "If disabled, the single Bonus Percentage below applies to everyone.",
    )
    bonus_percentage = fields.Float(
        string="Bonus Percentage (%)",
        digits=(5, 2),
        help="Used when 'Use Designation-wise Bonus %' is OFF. "
        "Applies the same percentage to all eligible employees.",
    )
    designation_rate_ids = fields.One2many(
        "festival.bonus.designation.rate",
        "template_id",
        string="Designation-wise Rates",
        help="Define a different bonus percentage per designation. "
        "Only used when 'Use Designation-wise Bonus %' is enabled.",
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

    # Eligibility Rule
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

    # Accounting fields
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
        "account.journal", string="Journal", domain="[('type', '=', 'general')]"
    )

    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True)

    # Eligibility Filter fields (used as default filters when adding employees)
    company_id = fields.Many2one("res.company", string="Company")
    department_id = fields.Many2one("hr.department", string="Department")
    job_id = fields.Many2one("hr.job", string="Designation")
    # employee_type = fields.Selection(
    #     [
    #         ("employee", "Employee"),
    #         ("student", "Student"),
    #         ("freelance", "Freelancer"),
    #     ],
    #     string="Employee Type",
    # )
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

    note = fields.Text(string="Notes")

    def get_percentage_for_employee(self, employee):
        self.ensure_one()
        if not self.use_designation_rates:
            return self.bonus_percentage or 0.0

        if not employee.job_id:
            return 0.0

        rate = self.designation_rate_ids.filtered(lambda r: r.job_id == employee.job_id)
        if rate:
            return rate[0].bonus_percentage
        return 0.0

    def name_get(self):
        result = []
        for rec in self:
            label = rec.name
            if not rec.use_designation_rates and rec.bonus_percentage:
                label = f"{rec.name} ({rec.bonus_percentage}%)"
            result.append((rec.id, label))
        return result

        # Account section
        # 1. Remove duplicate employees
        seen = set()
        to_unlink = self.env["festival.bonus.line"]
        for line in self.bonus_line_ids:
            if line.employee_id.id in seen:
                to_unlink |= line
            else:
                seen.add(line.employee_id.id)
        if to_unlink:
            to_unlink.unlink()

        # 2. Basic validation
        if not self.bonus_line_ids:
            raise UserError(_("Please add employees before confirming."))

        if not self.expense_account_id or not self.payable_account_id:
            raise UserError(
                _("Please configure the Expense and Payable accounts first.")
            )

        if self.total_bonus <= 0:
            raise UserError(_("Total bonus amount must be greater than zero."))

        # 3. Prepare journal lines
        move_lines = []

        # Separate debit line for each employee
        for line in self.bonus_line_ids:
            move_lines.append(
                (
                    0,
                    0,
                    {
                        "name": f"{self.name}",
                        "partner_id": line.employee_id.work_contact_id.id,
                        "account_id": self.expense_account_id.id,
                        "debit": line.bonus_amount,
                        "credit": 0,
                    },
                )
            )

        # Total amount for a credit line
        move_lines.append(
            (
                0,
                0,
                {
                    "name": f"Total Festival Bonus: {self.name}",
                    "account_id": self.payable_account_id.id,
                    "debit": 0,
                    "credit": self.total_bonus,
                },
            )
        )

        # 4. Create journal entry
        move_vals = {
            "journal_id": self.journal_id.id,
            "date": fields.Date.today(),
            "ref": _("Festival Bonus: ") + self.name,
            "state": "draft",
            "line_ids": move_lines,
        }

        move = self.env["account.move"].create(move_vals)
        self.move_id = move.id
        self.state = "confirmed"

    def action_reset_draft(self):
        self.ensure_one()

        # 1. If journal entry exists
        if self.move_id:
            # Condition: If the entry is 'posted', it cannot be reset.
            if self.move_id.state == "posted":
                raise UserError(
                    _("Festival bonuses cannot be reset if there are posted entries!")
                )

            # Condition: If the entry is not in 'cancel' mode, it cannot be reset.
            if self.move_id.state != "cancel":
                raise UserError(
                    _(
                        "Festival bonuses cannot be reset if the journal entry is not in 'Cancel' mode!"
                    )
                )

            # Condition: If the entry is in 'cancel' mode, it can be reset.
            self.move_id.unlink()
            self.move_id = False

        self.state = "draft"
