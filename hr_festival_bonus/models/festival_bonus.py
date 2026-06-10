from odoo import fields, models

class FestivalBonusBatch(models.Model):
    _name = 'festival.bonus.batch'
    _description = 'Festival Bonus Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
    )

    bonus_date = fields.Date(
        string='Bonus Date',
        required=True,
    )

    bonus_percentage = fields.Float(
        string='Bonus Percentage',
        required=True,
    )

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
        ],
        string='Status',
        default='draft',
        tracking=True,
    )

    line_ids = fields.One2many(
        'festival.bonus.line',
        'batch_id',
        string='Bonus Lines',
    )

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'


class FestivalBonusLine(models.Model):
    _name = 'festival.bonus.line'
    _description = 'Festival Bonus Line'


    batch_id = fields.Many2one(
        'festival.bonus.batch',
        string='Batch',
        required=True,
        ondelete='cascade',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
    )

    basic_salary = fields.Float(
        string='Basic Salary',
    )

    bonus_amount = fields.Float(
        string='Bonus Amount',
    )

