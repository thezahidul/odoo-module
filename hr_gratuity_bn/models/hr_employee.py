from odoo import models, fields, api
from datetime import date

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # এইচআর কনফিগারেশন ফিল্ড
    is_gratuity_eligible = fields.Boolean(string="Gratuity Enabled?", default=True)
    min_service_years = fields.Integer(string="Min. Service Years", default=1)
    
    # ইনপুট ফিল্ড
    manual_joining_date = fields.Date(string="Joining Date")
    manual_basic_salary = fields.Float(string="Monthly Basic Salary")
    
    # আউটপুট
    gratuity_amount = fields.Float(string="Total Gratuity Payable", compute="_compute_gratuity", store=True)

    @api.depends('manual_joining_date', 'manual_basic_salary', 'employee_type', 'is_gratuity_eligible', 'min_service_years')
    def _compute_gratuity(self):
        for employee in self:
            # কন্ডিশন ১: এইচআর কি গ্র্যাচুইটি এনাবেল করেছে?
            if not employee.is_gratuity_eligible:
                employee.gratuity_amount = 0.0
                continue

            # কন্ডিশন ২: Target Group (Employee Type == Employee)
            # নোট: Contract Type 'Full-Time' ফিল্ডটি hr_contract এর। 
            # যেহেতু সেটি নেই, আমরা আপাতত employee_type দিয়ে চেক করছি।
            if employee.employee_type != 'employee':
                employee.gratuity_amount = 0.0
                continue

            if employee.manual_joining_date and employee.manual_basic_salary > 0:
                diff = (date.today() - employee.manual_joining_date).days
                total_years_raw = diff / 365.25
                
                # কন্ডিশন ৩: Minimum Service পূর্ণ হয়েছে কি না
                if total_years_raw < employee.min_service_years:
                    employee.gratuity_amount = 0.0
                    continue

                # ১৮০ দিনের রাউন্ডিং লজিক
                years = diff // 365
                remaining_days = diff % 365
                adj_years = years + 1 if remaining_days >= 180 else years
                
                # স্ল্যাব লজিক (১-৫ বছর: ১.০, ৫+ বছর: ১.৫)
                factor = 1.0 if adj_years <= 5 else 1.5
                employee.gratuity_amount = (employee.manual_basic_salary * factor) * adj_years
            else:
                employee.gratuity_amount = 0.0