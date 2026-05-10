from odoo import models, fields, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    is_gratuity_eligible = fields.Boolean(string="Gratuity Enabled?", default=True)
    min_service_years = fields.Integer(string="Min. Service Years", default=1)
    manual_joining_date = fields.Date(string="Joining Date")
    manual_basic_salary = fields.Float(string="Monthly Basic Salary")
    gratuity_amount = fields.Float(string="Total Gratuity Payable", compute="_compute_gratuity", store=True)

    # ওডু ১৯-এ যেসব ফিল্ড আপনার মডেলে নেই সেগুলোকে depends-এ রাখা যাবে না
    @api.depends('manual_joining_date', 'manual_basic_salary', 'employee_type', 'is_gratuity_eligible', 'min_service_years')
    def _compute_gratuity(self):
        for employee in self:
            # ১. এলিজিবিলিটি চেক
            if not employee.is_gratuity_eligible or employee.employee_type != 'employee':
                employee.gratuity_amount = 0.0
                continue

            # ২. কন্ট্রাক্ট টাইপ চেক (নিরাপদ পদ্ধতি)
            # hasattr ব্যবহার করছি যাতে ফিল্ড না থাকলে ক্রাশ না করে
            is_valid_contract = True
            if hasattr(employee, 'contract_id') and employee.contract_id:
                c_type = employee.contract_id.contract_type_id.name or ""
                if c_type not in ['Permanent', 'Full-Time', 'Full Time']:
                    is_valid_contract = False
            
            if not is_valid_contract:
                employee.gratuity_amount = 0.0
                continue

            # ৩. ক্যালকুলেশন শুরু
            if employee.manual_joining_date and employee.manual_basic_salary > 0:
                diff = (date.today() - employee.manual_joining_date).days
                
                # ৫. Minimum Service Years চেক
                if (diff / 365.25) < employee.min_service_years:
                    employee.gratuity_amount = 0.0
                    continue

                years = diff // 365
                remaining_days = diff % 365
                adj_years = years + 1 if remaining_days >= 180 else years
                
                factor = 1.0 if adj_years <= 5 else 1.5
                employee.gratuity_amount = (employee.manual_basic_salary * factor) * adj_years
            else:
                employee.gratuity_amount = 0.0