from odoo import models, fields, api

class FestivalBonusLine(models.Model):
    _name = 'festival.bonus.line'
    _description = 'Festival Bonus Lines'

    bonus_id = fields.Many2one('festival.bonus.config', ondelete='cascade', string="Bonus Configuration")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    
    basic_salary = fields.Monetary(string="Basic Salary", currency_field='currency_id')
    joining_date = fields.Date(string="Joining Date")
    
    currency_id = fields.Many2one('res.currency', related='bonus_id.company_id.currency_id')
    bonus_amount = fields.Monetary(string="Bonus Amount", currency_field='currency_id')

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            employee = self.employee_id
            
            # hr.contract available আছে কিনা check করো
            if 'hr.contract' in self.env:
                contract = self.env['hr.contract'].search([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'open')
                ], limit=1)
                
                if contract:
                    self.basic_salary = contract.wage
                    self.joining_date = contract.date_start
                    return

            # Fallback: employee থেকে সরাসরি নাও
            self.joining_date = employee.joining_date \
                if hasattr(employee, 'joining_date') else False
            self.basic_salary = 0.0  # manually enter করতে হবে
        else:
            self.basic_salary = 0.0
            self.joining_date = False