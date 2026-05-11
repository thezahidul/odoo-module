from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_gratuity_eligible = fields.Boolean(
        string="Gratuity Enabled?", 
        default=False, 
        tracking=True
    )
    can_enable_gratuity = fields.Boolean(
        compute="_compute_can_enable_gratuity", 
        store=True
    )
    min_service_years = fields.Integer(
        string="Min. Service Years", 
        default=1
    )
    gratuity_amount = fields.Float(
        string="Total Gratuity Payable", 
        compute="_compute_gratuity", 
        store=True,
        digits=(16, 2)
    )

    @api.depends('employee_type', 'contract_type_id')
    def _compute_can_enable_gratuity(self):
        # Valid contract names list for faster lookup
        VALID_CONTRACTS = {'Permanent', 'Full-Time', 'Full Time'}
        for employee in self:
            c_type_name = employee.contract_type_id.name or ""
            is_eligible = (
                employee.employee_type == 'employee' and 
                c_type_name in VALID_CONTRACTS
            )
            employee.can_enable_gratuity = is_eligible
            # Reset eligibility if criteria no longer met
            if not is_eligible:
                employee.is_gratuity_eligible = False

    @api.depends('contract_date_start', 'wage', 'is_gratuity_eligible', 
                 'min_service_years', 'departure_date')
    def _compute_gratuity(self):
        for employee in self:
            # Defensive checks to avoid errors and unnecessary calculations
            if not employee.is_gratuity_eligible or not employee.contract_date_start:
                employee.gratuity_amount = 0.0
                continue

            wage = employee.wage or 0.0
            if wage <= 0:
                employee.gratuity_amount = 0.0
                continue

            start_date = employee.contract_date_start
            end_date = employee.departure_date or date.today()

            # Using relativedelta for precise year/day calculation
            rdiff = relativedelta(end_date, start_date)
            total_days = (end_date - start_date).days
            
            # Simple check for minimum service years
            if rdiff.years < employee.min_service_years:
                employee.gratuity_amount = 0.0
                continue

            # 180-day rounding rule logic
            # If remaining days in the last year are 180 or more, count as a full year
            years = total_days // 365
            remaining_days = total_days % 365
            
            final_years = years + 1 if remaining_days >= 180 else years
            
            if final_years <= 0:
                employee.gratuity_amount = 0.0
                continue

            # Slab logic: 1.0 factor for first 5 years, 1.5 factor for more than 5 years
            factor = 1.0 if final_years <= 5 else 1.5
            
            employee.gratuity_amount = (wage * factor) * final_years