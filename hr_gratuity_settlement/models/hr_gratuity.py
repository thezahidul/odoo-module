from odoo import models, fields, api, _
from datetime import date
from dateutil.relativedelta import relativedelta

class HrGratuitySettlement(models.Model):
    _name = 'hr.gratuity.settlement'
    _description = 'Gratuity Settlement'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)

    joining_date = fields.Date(string='Joining Date', tracking=True, required=True)
    last_working_day = fields.Date(string='Last Working Day', tracking=True, required=True, default=fields.Date.today)
    gross_wage = fields.Monetary(string='Gross Wage', currency_field='currency_id', tracking=True, required=True)

    # ✅ নতুন NBR ট্যাক্স কনফিগ ফিল্ডস
    is_nbr_approved = fields.Boolean(
        string='NBR Approved Gratuity Fund?',
        default=True,
        tracking=True,
        help="NBR অনুমোদিত ফান্ড হলে ২.৫ কোটি পর্যন্ত ট্যাক্স ফ্রি"
    )
    gratuity_exemption_limit = fields.Monetary(
        string='Tax Exemption Limit',
        currency_field='currency_id',
        default=25000000.0,
        tracking=True,
        help="NBR অনুমোদিত ক্ষেত্রে ট্যাক্স ফ্রি সীমা (ডিফল্ট: ২.৫ কোটি)"
    )
    gratuity_tax_percent = fields.Float(
        string='Tax Rate (%)',
        default=5.0,
        tracking=True,
        help="গ্র্যাচুইটির উপর প্রযোজ্য ট্যাক্স হার (ডিফল্ট: ৫%)"
    )

    # রেজাল্ট ফিল্ডস
    gratuity_amount = fields.Monetary(string='Gross Gratuity', compute='_compute_gratuity_totals', store=True, currency_field='currency_id')
    taxable_amount = fields.Monetary(string='Taxable Portion', compute='_compute_gratuity_totals', store=True, currency_field='currency_id')
    tax_deduction = fields.Monetary(string='Income Tax / TDS', compute='_compute_gratuity_totals', store=True, currency_field='currency_id')
    net_payable = fields.Monetary(string='Net Payable Settlement', compute='_compute_gratuity_totals', store=True, currency_field='currency_id')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Verified'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', tracking=True)

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.joining_date = self.employee_id.create_date.date() if self.employee_id.create_date else fields.Date.today()

    @api.model_create_multi
    def create(self, vals_list):
        current_year = date.today().year
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                record_count = self.search_count([('create_date', '>=', f'{current_year}-01-01')])
                next_number = str(record_count + 1).zfill(4)
                vals['name'] = f"GRF/{current_year}/{next_number}"
        return super().create(vals_list)

    # ✅ is_nbr_approved ও gratuity_exemption_limit এখন depends-এ যুক্ত
    @api.depends('joining_date', 'last_working_day', 'gross_wage', 'is_nbr_approved', 'gratuity_exemption_limit', 'gratuity_tax_percent')
    def _compute_gratuity_totals(self):
        for record in self:
            if record.joining_date and record.last_working_day and record.gross_wage > 0:
                d1 = fields.Date.from_string(record.joining_date)
                d2 = fields.Date.from_string(record.last_working_day)

                diff = relativedelta(d2, d1)
                years = diff.years
                remaining_days = (d2 - (d1 + relativedelta(years=years))).days
                if remaining_days >= 180:
                    years += 1

                if years >= 5:
                    record.gratuity_amount = record.gross_wage * 2 * years
                else:
                    record.gratuity_amount = record.gross_wage * years

                # ✅ NBR approved হলে exemption limit ব্যবহার করো, না হলে পুরোটাই taxable
                if record.is_nbr_approved and record.gratuity_amount > record.gratuity_exemption_limit:
                    record.taxable_amount = record.gratuity_amount - record.gratuity_exemption_limit
                elif not record.is_nbr_approved:
                    record.taxable_amount = record.gratuity_amount
                else:
                    record.taxable_amount = 0.0

                # ✅ gratuity_tax_percent ব্যবহার করে dynamic tax calculation
                tax_rate = (record.gratuity_tax_percent or 0.0) / 100.0
                record.tax_deduction = record.taxable_amount * tax_rate
                record.net_payable = record.gratuity_amount - record.tax_deduction
            else:
                record.gratuity_amount = 0.0
                record.taxable_amount = 0.0
                record.tax_deduction = 0.0
                record.net_payable = 0.0

    def action_verify(self): self.write({'state': 'verify'})
    def action_approve(self): self.write({'state': 'approve'})
    def action_cancel(self): self.write({'state': 'cancel'})
    def action_draft(self): self.write({'state': 'draft'})