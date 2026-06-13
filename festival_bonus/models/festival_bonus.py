from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FestivalBonusConfig(models.Model):
    _name = "festival.bonus.config"
    _description = "Festival Bonus Configuration"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "bonus_year desc, bonus_month desc"

    name = fields.Char(string="Festival Name", required=True, tracking=True)

    bonus_month = fields.Selection(
        [
            ("1", "January"),
            ("2", "February"),
            ("3", "March"),
            ("4", "April"),
            ("5", "May"),
            ("6", "June"),
            ("7", "July"),
            ("8", "August"),
            ("9", "September"),
            ("10", "October"),
            ("11", "November"),
            ("12", "December"),
        ],
        string="Month",
        required=True,
        default=lambda self: str(fields.Date.today().month),
        tracking=True,
    )
    bonus_year = fields.Integer(
        string="Year",
        required=True,
        default=lambda self: fields.Date.today().year,
        tracking=True,
    )
    bonus_percentage = fields.Float(
        string="Bonus Percentage (%)",
        digits=(5, 2),
        tracking=True,
    )
    min_service_months = fields.Integer(
        string="Minimum Service (Months)",
        default=6,
        tracking=True,
        help="Minimum months of service required to be eligible for bonus",
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
        tracking=True,
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
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
    )
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

    @api.depends("bonus_line_ids.bonus_amount")
    def _compute_total_bonus(self):
        for rec in self:
            rec.total_bonus = sum(rec.bonus_line_ids.mapped("bonus_amount"))

    @api.onchange("salary_base")
    def _onchange_salary_base(self):
        """salary_base change হলে সব existing lines update করো"""
        if not self.bonus_line_ids:
            return
        for line in self.bonus_line_ids:
            if not line.employee_id:
                continue
            line.salary_base_amount = line._get_salary_from_payslip(
                line.employee_id,
                self.salary_base,
            )
            line._compute_bonus_amount()

    def action_confirm_bonus(self):
        self.ensure_one()
        if not self.bonus_line_ids:
            raise UserError(_("Please add employees before confirming."))
        self.state = "confirmed"

    def action_reset_draft(self):
        self.ensure_one()
        self.state = "draft"

    def action_confirm_bonus(self):
        self.ensure_one()
        if not self.bonus_line_ids:
            raise UserError(_("Please add employees before confirming."))

        if not self.expense_account_id or not self.payable_account_id:
            raise UserError(
                _("Please configure the Expense and Payable accounts first.")
            )

        move_vals = {
            "journal_id": self.journal_id.id,
            "date": fields.Date.today(),
            "ref": _("Festival Bonus: ") + self.name,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": self.name,
                        "account_id": self.expense_account_id.id,
                        "debit": self.total_bonus,
                        "credit": 0,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.name,
                        "account_id": self.payable_account_id.id,
                        "debit": 0,
                        "credit": self.total_bonus,
                    },
                ),
            ],
        }
        self.env["account.move"].create(move_vals).action_post()
        self.state = "confirmed"
