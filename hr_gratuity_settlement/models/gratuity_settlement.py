from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta


class GratuitySettlement(models.Model):
    _name = "hr.gratuity.settlement"
    _description = "Gratuity Settlement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    # ===== Basic Information =====
    name = fields.Char(
        string="Settlement #",
        readonly=True,
        copy=False,
        default=lambda self: "NEW",
        tracking=True
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        tracking=True,
        ondelete="cascade"
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        tracking=True
    )

    # ===== Date Fields =====
    joining_date = fields.Date(
        string="Joining Date",
        required=True,
        tracking=True
    )
    resignation_date = fields.Date(
        string="Resignation Date",
        tracking=True
    )

    # ===== Service Period Calculation =====
    service_years = fields.Float(
        string="Service (Years)",
        compute="_compute_service_period",
        store=True,
        tracking=True
    )
    service_days = fields.Integer(
        string="Service (Days)",
        compute="_compute_service_period",
        store=True
    )
    min_service_years = fields.Integer(
        string="Min. Service Required (Years)",
        default=1,
        tracking=True
    )

    # ===== Eligibility =====
    is_eligible = fields.Boolean(
        string="Eligible for Gratuity",
        compute="_compute_eligibility",
        store=True,
        tracking=True
    )

    # ===== Wage & Slab =====
    gross_wage = fields.Float(
        string="Monthly Gross Wage",
        required=True,
        digits=(16, 2),
        tracking=True
    )
    slab_factor = fields.Float(
        string="Slab Factor",
        compute="_compute_slab_factor",
        store=True,
        tracking=True
    )

    # ===== Tax Configuration =====
    is_nbr_approved = fields.Boolean(
        string="NBR Tax Exemption Approved",
        default=False,
        tracking=True
    )
    gratuity_tax_percent = fields.Float(
        string="Tax Rate (%)",
        default=10.0,
        tracking=True
    )
    gratuity_exemption_limit = fields.Float(
        string="Tax Exemption Limit",
        default=25000000.0,
        digits=(16, 2),
        tracking=True
    )

    # ===== Gratuity Calculation Results =====
    gross_gratuity = fields.Float(
        string="Gross Gratuity Amount",
        compute="_compute_gratuity_totals",
        store=True,
        digits=(16, 2),
        tracking=True
    )
    taxable_amount = fields.Float(
        string="Taxable Portion",
        compute="_compute_gratuity_totals",
        store=True,
        digits=(16, 2),
        tracking=True
    )
    tax_deduction = fields.Float(
        string="Tax Deduction",
        compute="_compute_gratuity_totals",
        store=True,
        digits=(16, 2),
        tracking=True
    )
    net_payable = fields.Float(
        string="Net Payable Amount",
        compute="_compute_gratuity_totals",
        store=True,
        digits=(16, 2),
        tracking=True
    )

    # ===== Additional Fields =====
    notes = fields.Text(
        string="Notes",
        tracking=True
    )
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
            ("paid", "Paid"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        readonly=True,
        tracking=True
    )

    # ===== System Fields (inherited from mail.thread) =====
    create_date = fields.Datetime(string="Created On", readonly=True)
    create_uid = fields.Many2one("res.users", string="Created By", readonly=True)
    write_date = fields.Datetime(string="Last Modified On", readonly=True)
    write_uid = fields.Many2one("res.users", string="Last Modified By", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "NEW") == "NEW":
                vals["name"] = self.env["ir.sequence"].next_by_code("hr.gratuity.settlement") or "NEW"
        return super().create(vals_list)

    @api.depends("joining_date", "resignation_date")
    def _compute_service_period(self):
        """Calculate service period in years and days"""
        for record in self:
            if not record.joining_date:
                record.service_years = 0.0
                record.service_days = 0
                continue

            end_date = record.resignation_date or date.today()
            start_date = record.joining_date

            # Calculate total days
            total_days = (end_date - start_date).days

            # Using relativedelta for precise calculation
            diff = relativedelta(end_date, start_date)

            # BD Law: 180-day rounding rule
            years = total_days // 365
            final_years = years + 1 if (total_days % 365) >= 180 else years

            record.service_years = float(final_years) if final_years > 0 else 0.0
            record.service_days = total_days

    @api.depends("service_years", "min_service_years")
    def _compute_eligibility(self):
        """Check if employee is eligible for gratuity"""
        for record in self:
            record.is_eligible = record.service_years >= record.min_service_years

    @api.depends("service_years")
    def _compute_slab_factor(self):
        """
        Calculate slab factor based on service years
        BD Law: 1.0 for <= 5 years, 1.5 for > 5 years
        """
        for record in self:
            if record.service_years <= 5:
                record.slab_factor = 1.0
            else:
                record.slab_factor = 1.5

    @api.depends(
        "is_eligible",
        "gross_wage",
        "slab_factor",
        "service_years",
        "is_nbr_approved",
        "gratuity_exemption_limit",
        "gratuity_tax_percent"
    )
    def _compute_gratuity_totals(self):
        """Calculate gratuity amounts"""
        for record in self:
            # Reset if not eligible or missing data
            if not record.is_eligible or record.gross_wage <= 0:
                record.gross_gratuity = 0.0
                record.taxable_amount = 0.0
                record.tax_deduction = 0.0
                record.net_payable = 0.0
                continue

            # Calculate gross gratuity
            gross_amount = (record.gross_wage * record.slab_factor) * record.service_years
            record.gross_gratuity = gross_amount

            # Tax calculation
            taxable_income = 0.0
            if record.is_nbr_approved:
                # Only amount exceeding limit is taxable
                if gross_amount > record.gratuity_exemption_limit:
                    taxable_income = gross_amount - record.gratuity_exemption_limit
            else:
                # Entire amount is taxable if not NBR approved
                taxable_income = gross_amount

            record.taxable_amount = taxable_income
            record.tax_deduction = (taxable_income * record.gratuity_tax_percent) / 100.0
            record.net_payable = gross_amount - record.tax_deduction

    # ===== Workflow Actions =====
    def action_submit(self):
        """Submit settlement for approval"""
        for record in self:
            if record.state == "draft":
                record.state = "submitted"

    def action_approve(self):
        """Approve settlement"""
        for record in self:
            if record.state == "submitted":
                record.state = "approved"

    def action_mark_paid(self):
        """Mark settlement as paid"""
        for record in self:
            if record.state == "approved":
                record.state = "paid"

    def action_cancel(self):
        """Cancel settlement"""
        for record in self:
            if record.state in ["draft", "submitted", "approved"]:
                record.state = "cancelled"

    def action_reset_to_draft(self):
        """Reset to draft (for corrections)"""
        for record in self:
            if record.state == "cancelled":
                record.state = "draft"
