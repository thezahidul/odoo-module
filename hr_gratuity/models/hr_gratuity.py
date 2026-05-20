# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from dateutil.relativedelta import relativedelta
from datetime import date
import math


class HrGratuityPolicy(models.Model):
    """
    গ্লোবাল বা কোম্পানিভিত্তিক গ্র্যাচুইটি পলিসি কনফিগারেশন মডেল।
    """
    _name = 'hr.gratuity.policy'
    _description = 'HR Gratuity Policy Configuration'
    _order = 'name asc'

    name = fields.Char(string='Policy Name', required=True, help="e.g., Bangladesh Labor Law 2006")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True)
    
    days_per_year_below_5 = fields.Integer(string='Days/Year (1–5 Years)', default=30)
    days_per_year_above_5 = fields.Integer(string='Days/Year (5+ Years)', default=45)
    working_days_per_month = fields.Integer(string='Working Days/Month', default=26)
    min_service_years = fields.Integer(string='Minimum Service Years', default=1)
    
    rounding_policy = fields.Selection([
        ('bd_law', 'BD Law (>= 6 Months = 1 Year)'),
        ('actual', 'Actual Fraction (No Rounding)'),
        ('floor', 'Complete Years Only (Ignore Months)')
    ], string='Rounding Policy', default='bd_law', required=True)

    # ─── পলিসির ভেতরে ট্যাক্স সেটিংস ───
    is_nbr_approved = fields.Boolean(string='NBR Approved?', default=True, help="If checked, tax exemption limit will apply.")
    tax_exemption_limit = fields.Monetary(string='Tax Exemption Limit', default=25000000.0, currency_field='currency_id')
    tax_rate = fields.Float(string='Tax Rate (%)', default=10.0, digits=(16, 2))
    
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', readonly=True)

    _sql_constraints = [
        ('company_policy_unique', 'unique(name, company_id)', 'Policy name must be unique per company!')
    ]


class HrGratuity(models.Model):
    _name = 'hr.gratuity'
    _description = 'HR Gratuity Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'name'

    # ─── Basic Info ──────────────────────────────────────────────────────────
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'), tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='restrict', tracking=True, index=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True, readonly=True)
    job_id = fields.Many2one('hr.job', string='Job Position', related='employee_id.job_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True, readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True, copy=False)

    # ─── Policy Selection ────────────────────────────────────────────────────
    policy_id = fields.Many2one('hr.gratuity.policy', string='Gratuity Policy', required=True, tracking=True, domain="[('company_id', '=', company_id)]")

    # ─── Service Period ──────────────────────────────────────────────────────
    joining_date = fields.Date(string='Joining Date', required=True, tracking=True)
    departure_date = fields.Date(string='Departure/Resignation Date', tracking=True)
    calculation_date = fields.Date(string='Calculation Date', default=fields.Date.today, required=True)
    service_years = fields.Float(string='Service Years', compute='_compute_service_years', store=True, digits=(16, 4))
    service_years_display = fields.Char(string='Service Duration', compute='_compute_service_years', store=True)

    # ─── Salary ──────────────────────────────────────────────────────────────
    gross_wage = fields.Monetary(string='Gross Wage', required=True, currency_field='currency_id', tracking=True)
    basic_percentage = fields.Float(string='Basic Salary Percentage (%)', default=60.0)
    basic_wage = fields.Monetary(string='Basic Wage', compute='_compute_basic_wage', store=True, currency_field='currency_id')

    # ─── Related Configuration Fields (Fetched from Selected Policy) ─────────
    min_service_years = fields.Integer(string='Minimum Service Years', related='policy_id.min_service_years', readonly=True)
    days_per_year_below_5 = fields.Integer(string='Days/Year (1–5 Years)', related='policy_id.days_per_year_below_5', readonly=True)
    days_per_year_above_5 = fields.Integer(string='Days/Year (5+ Years)', related='policy_id.days_per_year_above_5', readonly=True)
    working_days_per_month = fields.Integer(string='Working Days/Month', related='policy_id.working_days_per_month', readonly=True)
    rounding_policy = fields.Selection(related='policy_id.rounding_policy', readonly=True)

    # ─── Related Tax Fields (Fetched from Selected Policy) ───────────────────
    is_nbr_approved = fields.Boolean(string='NBR Approved?', related='policy_id.is_nbr_approved', readonly=True, store=True)
    tax_exemption_limit = fields.Monetary(string='Tax Exemption Limit', related='policy_id.tax_exemption_limit', readonly=True, store=True)
    tax_rate = fields.Float(string='Tax Rate (%)', related='policy_id.tax_rate', readonly=True, store=True)

    total_gratuity = fields.Monetary(string='Total Gratuity', compute='_compute_gratuity', store=True, currency_field='currency_id', tracking=True)
    gratuity_line_ids = fields.One2many('hr.gratuity.line', 'gratuity_id', string='Calculation Lines', readonly=True)

    taxable_portion = fields.Monetary(string='Taxable Portion', compute='_compute_tax', store=True, currency_field='currency_id')
    tds_amount = fields.Monetary(string='TDS (Tax Amount)', compute='_compute_tax', store=True, currency_field='currency_id', tracking=True)
    net_payout = fields.Monetary(string='Net Payment', compute='_compute_tax', store=True, currency_field='currency_id', tracking=True)

    # ─── Payment & Notes ─────────────────────────────────────────────────────
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
            
            joining_date = fields.Date.from_string(rec.joining_date)
            end_date = fields.Date.from_string(rec.departure_date or rec.calculation_date or date.today())
            
            if joining_date > end_date:
                rec.service_years = 0.0
                rec.service_years_display = '0 Years'
                continue

            delta = relativedelta(end_date, joining_date)
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

    @api.depends('service_years', 'basic_wage', 'policy_id')
    def _compute_gratuity(self):
        for rec in self:
            if isinstance(rec.id, int):
                rec.gratuity_line_ids.unlink()
            
            if not rec.policy_id or rec.service_years < rec.min_service_years or not rec.id:
                rec.total_gratuity = 0.0
                continue
                
            rec.total_gratuity = rec._calculate_bd_labor_law()

    def _calculate_bd_labor_law(self):
        self.ensure_one()
        if not self.working_days_per_month:
            return 0.0
        
        daily_wage = self.basic_wage / self.working_days_per_month
        lines = []
        
        raw_years = math.floor(self.service_years)
        fractional = self.service_years - raw_years
        
        if self.rounding_policy == 'bd_law':
            if fractional >= 0.5:
                final_payable_years = raw_years + 1
                duration_msg = f"{raw_years} Years + Fractional Year (>= 6 Months rounded up)"
            else:
                final_payable_years = raw_years
                duration_msg = f"{raw_years} Years (Fractional Year < 6 Months ignored)"
            
            if final_payable_years <= 0:
                return 0.0

            if final_payable_years > 5:
                days_per_year = self.days_per_year_above_5
                desc = f"Policy [{self.policy_id.name}]: {duration_msg} at {days_per_year} days/year"
            else:
                days_per_year = self.days_per_year_below_5
                desc = f"Policy [{self.policy_id.name}]: {duration_msg} at {days_per_year} days/year"
                
            amount = daily_wage * days_per_year * final_payable_years
            lines.append({
                'gratuity_id': self.id,
                'description': desc,
                'years': final_payable_years,
                'days_per_year': days_per_year,
                'daily_wage': daily_wage,
                'amount': amount,
            })

        elif self.rounding_policy == 'floor':
            final_payable_years = raw_years
            days_per_year = self.days_per_year_above_5 if final_payable_years > 5 else self.days_per_year_below_5
            amount = daily_wage * days_per_year * final_payable_years
            lines.append({
                'gratuity_id': self.id,
                'description': f"Policy [{self.policy_id.name}]: Complete years only ({final_payable_years} Years)",
                'years': final_payable_years,
                'days_per_year': days_per_year,
                'daily_wage': daily_wage,
                'amount': amount,
            })

        elif self.rounding_policy == 'actual':
            total_amount = 0.0
            below_5_part = min(self.service_years, 5.0)
            if below_5_part > 0:
                amt_1 = daily_wage * self.days_per_year_below_5 * below_5_part
                total_amount += amt_1
                lines.append({
                    'gratuity_id': self.id,
                    'description': f"Policy [{self.policy_id.name}]: Pro-rata (1-5 Years part)",
                    'years': below_5_part,
                    'days_per_year': self.days_per_year_below_5,
                    'daily_wage': daily_wage,
                    'amount': amt_1,
                })
            
            above_5_part = max(self.service_years - 5.0, 0.0)
            if above_5_part > 0:
                amt_2 = daily_wage * self.days_per_year_above_5 * above_5_part
                total_amount += amt_2
                lines.append({
                    'gratuity_id': self.id,
                    'description': f"Policy [{self.policy_id.name}]: Pro-rata (5+ Years part)",
                    'years': above_5_part,
                    'days_per_year': self.days_per_year_above_5,
                    'daily_wage': daily_wage,
                    'amount': amt_2,
                })
            amount = total_amount

        self.env['hr.gratuity.line'].create(lines)
        return round(amount, 2)

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
            default_policy = self.env['hr.gratuity.policy'].search([
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            if default_policy:
                self.policy_id = default_policy

            if hasattr(self.employee_id, 'date_start') and self.employee_id.date_start:
                self.joining_date = self.employee_id.date_start
            elif hasattr(self.employee_id, 'contract_id') and self.employee_id.contract_id.date_start:
                self.joining_date = self.employee_id.contract_id.date_start
            else:
                self.joining_date = fields.Date.today()

            if hasattr(self.employee_id, 'wage') and self.employee_id.wage:
                self.gross_wage = self.employee_id.wage
            elif hasattr(self.employee_id, 'contract_id') and self.employee_id.contract_id.wage:
                self.gross_wage = self.employee_id.contract_id.wage
        else:
            self.gross_wage = 0.0
            self.joining_date = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.gratuity') or _('New')
        return super().create(vals_list)

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
                raise ValidationError(_('An active Gratuity record already exists for this employee!'))

    def action_confirm(self):
        for rec in self:
            if rec.service_years < rec.min_service_years:
                raise UserError(_(
                    f"The employee's service length is only {rec.service_years:.2f} years. "
                    f"A minimum of {rec.min_service_years} years is required to qualify under [{rec.policy_id.name}]."
                ))
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
        return self.env.ref('hr_gratuity.action_report_gratuity_settlement').report_action(self)


class HrGratuityLine(models.Model):
    _name = 'hr.gratuity.line'
    _description = 'Gratuity Calculation Line'
    _order = 'id asc'

    gratuity_id = fields.Many2one('hr.gratuity', string='Gratuity', required=True, ondelete='cascade')
    description = fields.Char(string='Description', required=True)
    years = fields.Float(string='Years', digits=(16, 4))
    days_per_year = fields.Integer(string='Days/Year')
    daily_wage = fields.Float(string='Daily Wage', digits=(16, 4))
    amount = fields.Float(string='Amount', digits=(16, 2))