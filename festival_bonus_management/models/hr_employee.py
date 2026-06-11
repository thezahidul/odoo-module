from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    bonus_line_ids = fields.One2many('festival.bonus.line', 'employee_id', string='Bonus Records')
    
    bonus_count = fields.Integer(string='Bonus Count', compute='_compute_bonus_count')

    @api.depends('bonus_line_ids')
    def _compute_bonus_count(self):
        for employee in self:
            employee.bonus_count = len(employee.bonus_line_ids)

    def action_open_festival_bonus(self):
        self.ensure_one()
        return {
            'name': 'Festival Bonus Records',
            'type': 'ir.actions.act_window',
            'res_model': 'festival.bonus.line',
            'view_mode': 'list',
            'domain': [('employee_id', '=', self.id)],
            'target': 'current',
        }