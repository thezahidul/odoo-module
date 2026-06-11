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
        string="Bonus Percentage (%)", digits=(5, 2), tracking=True
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed")],
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
        "festival.bonus.line", "bonus_id", string="Bonus Lines"
    )
    total_bonus = fields.Monetary(
        string="Total Bonus",
        currency_field="currency_id",
        compute="_compute_total_bonus",
        store=True,
    )

    min_service_months = fields.Integer(
        string="Minimum Service (Months)",
        default=6,
        help="Minimum months of service required to be eligible for bonus",
        tracking=True,
    )

    @api.depends("bonus_line_ids.bonus_amount")
    def _compute_total_bonus(self):
        for rec in self:
            rec.total_bonus = sum(rec.bonus_line_ids.mapped("bonus_amount"))

    def action_confirm_bonus(self):
        self.ensure_one()
        if not self.bonus_line_ids:
            raise UserError(_("Please add employees before confirming."))
        self.state = "confirmed"
