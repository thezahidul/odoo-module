# from odoo import models,fields,api
# from datetime import date
# from dateutil.relativedelta import relativedelta

# class HrEmployee(models.Model):
#     _inherit='hr.employee'

#     is_gratuity_eligible=fields.Boolean(
#         string="Gratuity Enabled?",
#         default=False,
#         tracking=True
#     )

#     can_enable_gratuity=fields.Boolean(
#         compute="_compute_can_enable_gratuity",
#         store=True
#     )

#     min_service_years=fields.Integer(
#         string="Min. Service Years",
#         defaultl=1
#     )
    
#     #configuration fields
#     is_nbr_approved=fields.Boolean(
#         string="Is NBR Approved?",
#         default=True,
#         help="If checked, the 2.5 Crore exemption applies per NBR rules."
#     )

#     gratuity_tax_percent=fields.Float(
#         string="Tax Rate (%)",
#         default=10.0
#     )

#     gratutiy_exemption_lmit=fields.Float(
#         string="Tax Exemption Limit",
#         default=25000000.0
#     )

#     #Result Fields
#     gratuity_amount=fields.Float(
#         string="Gross Gratuity",
#         compute="_compute_gratuity_totals",
#         store=True,
#         digits=(16,2)
#     )

#     gratuity_taxable_amount=fields.Float(
#         string="Tax Deduction",
#         compute="_compute_gratuity_totals",
#         store= True,
#         help="The protion of gratuity subject to tax after exemption."
#     )
#     gratuity_tax_amount=fields.Float(
#         string="Tax Deduction",
#         compute="_compute_gratuity_totals",
#         store=True,
#         digits=(16,2)
#     )

#     @api.depends('employee_type','contract_type_id')
#     def _compute_can_enable_gratuity(self):
#         VALID_CONTRACTS={'Permanent','Full-Time','Full Time'}
#         for employee in self:
#             c_type_name=employee.contract_type_id.name or ""
#             employee.can_enable_gratuity=(
#                 employee.employee_type=='employee' and c_type_name in VALID_CONTRACTS
#             )

#     @api.depends('contract_date_start','wage','is_gratuity_eligible','departure_date','is_nbr_approved','gratuity_tax_percent','gratuity_exemption_limit','min_service_years')
#     def _compute_gratuity_totals(self):
#         for employee in self:
#             if not employee.is_gratuity_eligible or not employee.contract_date_start or (employee.wage or 0.0)<=0:
#                 employee.update({
#                     'gratuity_amount':0.0,
#                     'gratuity_taxable_amount':0.0,
#                     'gratuity_tax_amount':0.0,
#                     'gratuity_tax_amount':0.0
#                 })
#                 continue
            
#             start_date=employee.contract_date_start
#             end_date=employee.departure_date or date.today()

#             #Using relativedelta for precise date difference
#             diff=relativedelta(end_date,start_date)
#             total_days=(end_date-start_date).days

#             #Minimum Service requirement for precise data difference
#             diff=relativedelta(end_date,start_date)
#             total_days=(end_date-start_date).days

#             #Minimum service requirement check
#             if diff.years < employee.min_service_years:
#                 employee.update({
#                     'gratuity_amount': 0.0,
#                     'gratuity_taxable_amount': 0.0,
#                     'gratuity_tax_amount': 0.0,
#                     'gratuity_net_payable': 0.0
#                 })
#                 continue
        
#             #BD law: 180-day rounding rule for service years
#             years=total_days//365
#             final_years=years+1 if (total_days%365)>= 180 else years

#             if final_years<=0:
#                 employee.gratuity_amount=0.0
#                 continue

#             #Slab Logic: 1.0 factor for <= 5 years, 1.5 factor for>5 years
#             factor=1.0 if final_years <= 5 else 1.5
#             gross_amount=(employee.wage*factor)*final_years
#             employee.gratuity_amount=self.gratuity_amount


