from odoo import models, fields, api
from datetime import date
from dateutil.relativedelta import relativedelta

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # --- Eligibility Fields ---
    is_gratuity_eligible = fields.Boolean(string="Gratuity Enabled?", default=False, tracking=True)
    can_enable_gratuity = fields.Boolean(compute="_compute_can_enable_gratuity", store=True)
    
    # এটি মিসিং ছিল, তাই এরর আসছিল
    min_service_years = fields.Integer(string="Min. Service Years", default=1)
    
    # --- Configuration Fields ---
    is_nbr_approved = fields.Boolean(string="Is NBR Approved?", default=True)
    gratuity_tax_percent = fields.Float(string="Tax Rate (%)", default=10.0)
    gratuity_exemption_limit = fields.Float(string="Tax Exemption Limit", default=25000000.0)

    # --- Result Fields ---
    gratuity_amount = fields.Float(string="Gross Gratuity", compute="_compute_gratuity_totals", store=True)
    gratuity_taxable_amount = fields.Float(
        string="Taxable Amount", 
        compute="_compute_gratuity_totals", 
        store=True,
        help="The portion of gratuity subject to tax after exemption."
    )
    gratuity_tax_amount = fields.Float(string="Tax Deduction", compute="_compute_gratuity_totals", store=True)
    gratuity_net_payable = fields.Float(string="Net Payout", compute="_compute_gratuity_totals", store=True)
    

    @api.depends('employee_type', 'contract_type_id')
    def _compute_can_enable_gratuity(self):
        VALID_CONTRACTS = {'Permanent', 'Full-Time', 'Full Time'}
        for employee in self:
            c_type_name = employee.contract_type_id.name or ""
            employee.can_enable_gratuity = employee.employee_type == 'employee' and c_type_name in VALID_CONTRACTS

    @api.depends('contract_date_start', 'wage', 'is_gratuity_eligible', 'departure_date', 
                 'is_nbr_approved', 'gratuity_tax_percent', 'gratuity_exemption_limit', 'min_service_years')
    def _compute_gratuity_totals(self):
        for employee in self:
            if not employee.is_gratuity_eligible or not employee.contract_date_start or (employee.wage or 0.0) <= 0:
                employee.gratuity_amount = employee.gratuity_tax_amount = employee.gratuity_net_payable = 0.0
                continue

            start_date = employee.contract_date_start
            end_date = employee.departure_date or date.today()
            
            # নিখুঁত বছর গণনার জন্য relativedelta সেরা
            diff = relativedelta(end_date, start_date)
            total_days = (end_date - start_date).days
            
            # মিনিমাম সার্ভিস চেক
            if diff.years < employee.min_service_years:
                employee.gratuity_amount = employee.gratuity_tax_amount = employee.gratuity_net_payable = 0.0
                continue

            # ১৮০ দিনের রাউন্ডিং নিয়ম
            years = total_days // 365
            final_years = years + 1 if (total_days % 365) >= 180 else years
            
            if final_years <= 0:
                employee.gratuity_amount = 0.0
                continue

            # স্ল্যাব লজিক
            factor = 1.0 if final_years <= 5 else 1.5
            gross_amount = (employee.wage * factor) * final_years
            employee.gratuity_amount = gross_amount

            # ট্যাক্স লজিক
            taxable_income = 0.0
            if employee.is_nbr_approved:
                # যদি গ্রস অ্যামাউন্ট ২.৫ কোটির বেশি হয়, শুধু বাড়তি অংশ ট্যাক্সেবল
                if employee.gratuity_amount > employee.gratuity_exemption_limit:
                    taxable_income = employee.gratuity_amount - employee.gratuity_exemption_limit
            else:
                # অনুমোদিত না হলে পুরো টাকাই ট্যাক্সেবল
                taxable_income = employee.gratuity_amount
            
            employee.gratuity_taxable_amount = taxable_income
            employee.gratuity_tax_amount = (taxable_income * employee.gratuity_tax_percent) / 100.0
            employee.gratuity_net_payable = employee.gratuity_amount - employee.gratuity_tax_amount