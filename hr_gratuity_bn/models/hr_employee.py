from odoo import models, fields, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_gratuity_eligible = fields.Boolean(string="Gratuity Enabled?", default=False)
    # এখন আমরা সরাসরি contract_type_id ব্যবহার করতে পারব
    can_enable_gratuity = fields.Boolean(compute="_compute_can_enable_gratuity")
    
    min_service_years = fields.Integer(string="Min. Service Years", default=1)
    manual_joining_date = fields.Date(string="Joining Date")
    manual_basic_salary = fields.Float(string="Monthly Basic Salary")
    gratuity_amount = fields.Float(string="Total Gratuity Payable", compute="_compute_gratuity", store=True)

    @api.depends('employee_type', 'contract_type_id')
    def _compute_can_enable_gratuity(self):
        for employee in self:
            # আপনার স্ক্রিনশট অনুযায়ী contract_type_id.name চেক করছি
            valid_types = ['Permanent', 'Full-Time', 'Full Time']
            c_type_name = employee.contract_type_id.name if employee.contract_type_id else ""
            
            # কন্ডিশন: Employee Type 'employee' এবং বৈধ Contract Type
            if employee.employee_type == 'employee' and c_type_name in valid_types:
                employee.can_enable_gratuity = True
            else:
                employee.can_enable_gratuity = False
                employee.is_gratuity_eligible = False

    @api.depends('manual_joining_date', 'manual_basic_salary', 'is_gratuity_eligible', 'min_service_years')
    def _compute_gratuity(self):
        for employee in self:
            if not employee.is_gratuity_eligible or not employee.manual_joining_date or employee.manual_basic_salary <= 0:
                employee.gratuity_amount = 0.0
                continue

            diff = (date.today() - employee.manual_joining_date).days
            if (diff / 365.25) < employee.min_service_years:
                employee.gratuity_amount = 0.0
                continue

            # ক্যালকুলেশন লজিক (১৮০ দিন নিয়ম)
            years = diff // 365
            remaining_days = diff % 365
            adj_years = years + 1 if remaining_days >= 180 else years
            
            factor = 1.0 if adj_years <= 5 else 1.5
            employee.gratuity_amount = (employee.manual_basic_salary * factor) * adj_years