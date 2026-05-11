from odoo import models, fields, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # গ্র্যাচুইটি কন্ডিশন ফিল্ড
    is_gratuity_eligible = fields.Boolean(string="Gratuity Enabled?", default=False)
    can_enable_gratuity = fields.Boolean(compute="_compute_can_enable_gratuity")
    min_service_years = fields.Integer(string="Min. Service Years", default=1)
    
    # ক্যালকুলেটেড অ্যামাউন্ট
    gratuity_amount = fields.Float(string="Total Gratuity Payable", compute="_compute_gratuity", store=True)

    @api.depends('employee_type', 'contract_type_id')
    def _compute_can_enable_gratuity(self):
        for employee in self:
            # স্ক্রিনশট অনুযায়ী কন্ডিশন চেক
            valid_contracts = ['Permanent', 'Full-Time', 'Full Time']
            c_type_name = employee.contract_type_id.name if employee.contract_type_id else ""
            
            if employee.employee_type == 'employee' and c_type_name in valid_contracts:
                employee.can_enable_gratuity = True
            else:
                employee.can_enable_gratuity = False
                employee.is_gratuity_eligible = False

    @api.depends('contract_date_start', 'wage', 'is_gratuity_eligible', 'min_service_years', 'departure_date')
    def _compute_gratuity(self):
        for employee in self:
            # স্ক্রিনশট অনুযায়ী wage এবং contract_date_start ব্যবহার করা হয়েছে
            if not employee.is_gratuity_eligible or not employee.contract_date_start or employee.wage <= 0:
                employee.gratuity_amount = 0.0
                continue

            # এন্ড ডেট লজিক: চাকরি ছাড়লে departure_date, নাহলে আজকের তারিখ
            end_date = employee.departure_date if employee.departure_date else date.today()
            
            # দিন গণনা
            diff = (end_date - employee.contract_date_start).days
            total_years_raw = diff / 365.25
            
            # মিনিমাম সার্ভিস চেক
            if total_years_raw < employee.min_service_years:
                employee.gratuity_amount = 0.0
                continue

            # ১৮০ দিনের রাউন্ডিং নিয়ম
            years = diff // 365
            remaining_days = diff % 365
            adj_years = years + 1 if remaining_days >= 180 else years
            
            # স্ল্যাব ও ফ্যাক্টর (১-৫ বছর: ১.০, ৫+ বছর: ১.৫)
            factor = 1.0 if adj_years <= 5 else 1.5
            employee.gratuity_amount = (employee.wage * factor) * adj_years


            