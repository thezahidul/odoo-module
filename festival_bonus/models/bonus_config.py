from odoo import models, fields, api

class FestivalBonusConfig(models.Model):
    _name = 'festival.bonus.config'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Festival Bonus Configuration'

    name = fields.Char(string="Festival Name", required=True, tracking=True)
    bonus_date = fields.Date(string="Payment Date")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft', tracking=True)
    
    # Links to Expense and Liability Accounts
    expense_account_id = fields.Many2one('account.account', string="Expense Account")
    payable_account_id = fields.Many2one('account.account', string="Payable Account")
    
    bonus_line_ids = fields.One2many('festival.bonus.line', 'bonus_id', string="Employees")

    def action_confirm(self):
        # Add your accounting entry logic here
        self.state = 'confirmed'