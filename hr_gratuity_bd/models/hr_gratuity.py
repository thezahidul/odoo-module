# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import date
import math


class HrGratuity(models.Model):
    """
    Gratuity Management according to Bangladesh Labor Law 2006.
    This is an independent model completely separated from the hr.employee model.

    BD Labor Law Formula:
      - 1–5 Years  : (Basic ÷ 26) × 30 days per year
      - 5+ Years   : (Basic ÷ 26) × 45 days per year
    """
    _name = 'hr.gratuity'
    _description = 'HR Gratuity - Bangladesh Labor Law'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    # ─── Basic Info ──────────────────────────────────────────────────────────

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New'),
        tracking=True,
    )

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
        ondelete='restrict',
        tracking=True,
        index=True,
    )

    department_id = fields.Many2one(
        comodel_name='hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True,
    )

    job_id = fields.Many2one(
        comodel_name='hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True,
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        readonly=True,
    )

    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True,
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        tracking=True,
        copy=False,
    )

    # ─── Service Period ──────────────────────────────────────────────────────

    joining_date = fields.Date(
        string='Joining Date',
        required=True,
        tracking=True,
    )

    departure_date = fields.Date(
        string='Departure/Resignation Date',
        tracking=True,
    )

    calculation_date = fields.Date(
        string='Calculation Date',
        default=fields.Date.today,
        required=True,
    )

    service_years = fields.Float(
        string='Service Years',
        compute='_compute_service_years',
        store=True,
        digits=(16, 4),
    )

    service_years_display = fields.Char(
        string='Service Duration',
        compute='_compute_service_years',
        store=True,
    )

    min_service_years = fields.Integer(
        string='Minimum Service Years',
        default=1,
    )

    # ─── Salary ──────────────────────────────────────────────────────────────

    gross_wage = fields.Monetary(
        string='Gross Wage',
        required=True,
        currency_field='currency_id',
        tracking=True,
    )

    basic_percentage = fields.Float(
        string='Basic Salary Percentage (%)',
        default=60.0,
    )

    basic_wage = fields.Monetary(
        string='Basic Wage',
        compute='_compute_basic_wage',
        store=True,
        currency_field='currency_id',
    )

    # ─── Calculation ─────────────────────────────────────────────────────────

    calculation_type = fields.Selection(
        selection=[
            ('bd_labor_law', 'BD Labor Law 2006'),
        ],
        string='Calculation Method',
        default='bd_labor_law',
        required=True,
    )

    days_per_year_below_5 = fields.Integer(
        string='Days/Year (1–5 Years)',
        default=30,
        help='BD Labor Law: 30 days/year for the first 5 years',
    )

    days_per_year_above_5 = fields.Integer(
        string='Days/Year (5+ Years)',
        default=45,
        help='BD Labor Law: 45 days/year for service extending past 5 years',
    )

    working_days_per_month = fields.Integer(
        string='Working Days/Month',
        default=26,
    )

    total_gratuity = fields.Monetary(
        string='Total Gratuity',
        compute='_compute_gratuity',
        store=True,
        currency_field='currency_id',
        tracking=True,
    )

    gratuity_line_ids = fields.One2many(
        comodel_name='hr.gratuity.line',
        inverse_name='gratuity_id',
        string='Calculation Lines',
        readonly=True,
    )

    # ─── Tax ─────────────────────────────────────────────────────────────────

    is_nbr_approved = fields.Boolean(
        string='NBR Approved?',
        default=True,
    )

    tax_exemption_limit = fields.Monetary(
        string='Tax Exemption Limit',
        default=25000000.0,
        currency_field='currency_id',
    )

    tax_rate = fields.Float(
        string='Tax Rate (%)',
        default=10.0,
        digits=(16, 2),
    )

    taxable_portion = fields.Monetary(
        string='Taxable Portion',
        compute='_compute_tax',
        store=True,
        currency_field='currency_id',
    )

    tds_amount = fields.Monetary(
        string='TDS (Tax Amount)',
        compute='_compute_tax',
        store=True,
        currency_field='currency_id',
        tracking=True,
    )

    net_payout = fields.Monetary(
        string='Net Payment',
        compute='_compute_tax',
        store=True,
        currency_field='currency_id',
        tracking=True,
    )

    # ─── Payment ─────────────────────────────────────────────────────────────

    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_reference = fields.Char(string='Payment Reference', tracking=True)
    notes = fields.Text(string='Notes')

    # ─── Computes ────────────────────────────────────────────────────────────

    @api.depends('joining_date', 'departure_date', 'calculation_date')
    def _compute_service_years(self):
        for rec in self:
            if not rec.joining_date:
                rec.service_years = 0.0
                rec.service_years_display = '0 Years'
                continue
            end_date = rec.departure_date or rec.calculation_date or date.today()
            delta = relativedelta(end_date, rec.joining_date)
            total_months = delta.years * 12 + delta.months
            rec.service_years = round(total_months / 12, 4)
            
            display = f'{delta.years} Years'
            if delta.months:
                display += f' {delta.months} Months'
            if delta.days:
                display += f' {delta.days} Days'
            rec.service_years_display = display

    @api.depends('gross_wage', 'basic_percentage')
    def _compute_basic_wage(self):
        for rec in self:
            rec.basic_wage = rec.gross_wage * (rec.basic_percentage / 100)

    @api.depends(
        'service_years', 'basic_wage', 'working_days_per_month',
        'days_per_year_below_5', 'days_per_year_above_5',
        'min_service_years',
    )
    def _compute_gratuity(self):
        for rec in self:
            # যদি রেকর্ডটি ডাটাবেজে অলরেডি সেভ করা থাকে, তবেই পুরাতন লাইন ডিলিট করবে
            if isinstance(rec.id, int):
                rec.gratuity_line_ids.unlink()
            
            # সার্ভিস পিরিয়ড কম হলে বা রেকর্ডটির আইডি এখনও না থাকলে (নতুন হলে) ক্যালকুলেশন স্কিপ করবে
            if rec.service_years < rec.min_service_years or not rec.id:
                rec.total_gratuity = 0.0
                continue
                
            rec.total_gratuity = rec._calculate_bd_labor_law()

    def _calculate_bd_labor_law(self):
        self.ensure_one()
        if not self.working_days_per_month:
            return 0.0
        daily_wage = self.basic_wage / self.working_days_per_month
        total = 0.0
        lines = []
        years = math.floor(self.service_years)
        fractional = self.service_years - years

        # 1–5 Years: 30 days/year
        below_5 = min(years, 5)
        if below_5 > 0:
            amount = daily_wage * self.days_per_year_below_5 * below_5
            total += amount
            lines.append({
                'gratuity_id': self.id,
                'description': f'First {below_5} Years ({self.days_per_year_below_5} days/year)',
                'years': below_5,
                'days_per_year': self.days_per_year_below_5,
                'daily_wage': daily_wage,
                'amount': amount,
            })

        # 5+ Years: 45 days/year
        above_5 = max(years - 5, 0)
        if above_5 > 0:
            amount = daily_wage * self.days_per_year_above_5 * above_5
            total += amount
            lines.append({
                'gratuity_id': self.id,
                'description': f'Next {above_5} Years ({self.days_per_year_above_5} days/year)',
                'years': above_5,
                'days_per_year': self.days_per_year_above_5,
                'daily_wage': daily_wage,
                'amount': amount,
            })

        # Fractional year (6+ months evaluated proportionally)
        if fractional >= 0.5:
            days = self.days_per_year_above_5 if years >= 5 else self.days_per_year_below_5
            amount = daily_wage * days * fractional
            total += amount
            lines.append({
                'gratuity_id': self.id,
                'description': f'Fractional Portion ({fractional:.2f} Years)',
                'years': fractional,
                'days_per_year': days,
                'daily_wage': daily_wage,
                'amount': amount,
            })

        self.env['hr.gratuity.line'].create(lines)
        return round(total, 2)

    @api.depends('total_gratuity', 'is_nbr_approved', 'tax_exemption_limit', 'tax_rate')
    def _compute_tax(self):
        for rec in self:
            if rec.is_nbr_approved:
                taxable = max(rec.total_gratuity - rec.tax_exemption_limit, 0)
            else:
                taxable = rec.total_gratuity
            tds = round(taxable * rec.tax_rate / 100, 2)
            rec.taxable_portion = round(taxable, 2)
            rec.tds_amount = tds
            rec.net_payout = round(rec.total_gratuity - tds, 2)

    # ─── Onchange ────────────────────────────────────────────────────────────

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.joining_date = self.employee_id.date_start
            # Fetch wage data from contract if hr_payroll is installed
            if 'hr.contract' in self.env:
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', self.employee_id.id),
                    ('state', '=', 'open'),
                ], limit=1)
                if contract:
                    self.gross_wage = contract.wage

    # ─── Sequence ────────────────────────────────────────────────────────────

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.gratuity') or _('New')
        return super().create(vals_list)

    # ─── Constraints ─────────────────────────────────────────────────────────

    @api.constrains('joining_date', 'departure_date')
    def _check_dates(self):
        for rec in self:
            if rec.departure_date and rec.joining_date:
                if rec.departure_date < rec.joining_date:
                    raise ValidationError(_('Departure date cannot be earlier than the joining date!'))

    @api.constrains('employee_id', 'state')
    def _check_duplicate_active(self):
        for rec in self:
            existing = self.search([
                ('employee_id', '=', rec.employee_id.id),
                ('state', 'not in', ['cancelled', 'paid']),
                ('id', '!=', rec.id),
            ])
            if existing:
                raise ValidationError(_(
                    'An active Gratuity record already exists for this employee!'
                ))

    # ─── State Actions ────────────────────────────────────────────────────────

    def action_confirm(self):
        for rec in self:
            if rec.service_years < rec.min_service_years:
                raise UserError(_(
                    f"The employee's service length is only {rec.service_years:.2f} years. "
                    f"A minimum of {rec.min_service_years} years is required to qualify for Gratuity."
                ))
            
            # কনফার্ম করার সময় ডাটাবেজে ID নিশ্চিত থাকে, তাই এখানে ক্যালকুলেশন কল করে দেওয়া নিরাপদ
            rec.total_gratuity = rec._calculate_bd_labor_law()
            rec.state = 'confirmed'

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_mark_paid(self):
        for rec in self:
            if not rec.payment_date:
                rec.payment_date = date.today()
            rec.state = 'paid'

    def action_cancel(self):
        for rec in self:
            if rec.state == 'paid':
                raise UserError(_('A paid Gratuity record cannot be cancelled!'))
            rec.state = 'cancelled'

    def action_reset_draft(self):
        self.write({'state': 'draft'})

    def action_print_settlement_report(self):
        return self.env.ref(
            'hr_gratuity_bd.action_report_gratuity_settlement'
        ).report_action(self)


class HrGratuityLine(models.Model):
    _name = 'hr.gratuity.line'
    _description = 'Gratuity Calculation Line'
    _order = 'id asc'

    gratuity_id = fields.Many2one(
        comodel_name='hr.gratuity',
        string='Gratuity',
        required=True,
        ondelete='cascade',
    )
    description = fields.Char(string='Description', required=True)
    years = fields.Float(string='Years', digits=(16, 4))
    days_per_year = fields.Integer(string='Days/Year')
    daily_wage = fields.Float(string='Daily Wage', digits=(16, 4))
    amount = fields.Float(string='Amount', digits=(16, 2))