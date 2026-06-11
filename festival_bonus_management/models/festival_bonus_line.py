from odoo import models, fields, api

class FestivalBonusLine(models.Model):
    _name = 'festival.bonus.line'
    _description = 'Festival Bonus Lines'

    bonus_id = fields.Many2one('festival.bonus.config', ondelete='cascade', string="Bonus Configuration")
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True)
    
    basic_salary = fields.Monetary(string="Basic Salary", currency_field='currency_id')
    joining_date = fields.Date(string="Joining Date")
    
    currency_id = fields.Many2one('res.currency', related='bonus_id.company_id.currency_id')
    bonus_amount = fields.Monetary(string="Bonus Amount", currency_field='currency_id', compute='_compute_bonus_amount', store=True)

    @api.depends('basic_salary', 'bonus_id.bonus_percentage')
    def _compute_bonus_amount(self):
        for line in self:
            if line.basic_salary and line.bonus_id.bonus_percentage:
                line.bonus_amount = line.basic_salary * line.bonus_id.bonus_percentage / 100
            else:
                line.bonus_amount = 0.0


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.basic_salary = self.employee_id.wage or 0.0
            self.joining_date = self.employee_id.contract_date_start or False
        else:
            self.basic_salary = 0.0
            self.joining_date = False