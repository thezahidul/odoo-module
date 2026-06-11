# models/festival_bonus.py
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FestivalBonusConfig(models.Model):
    _name = 'festival.bonus.config'
    _description = 'Festival Bonus Configuration'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Festival Name", required=True)
    bonus_date = fields.Date(string="Scheduled Payment Date", required=True)
    bonus_percentage = fields.Float(string="Bonus Percentage (%)")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft')
    
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.company)
    bonus_line_ids = fields.One2many('festival.bonus.line', 'bonus_id', string="Bonus Lines")
    
    # 2. Compute methods (if any)
    
    # 3. Business Logic Methods (Action buttons)
    def action_confirm_bonus(self):
        self.ensure_one()
        # Validation logic
        if not self.bonus_line_ids:
            raise UserError(_("Please add employees before confirming."))
        
        # Accounting logic (as discussed previously)
        self.state = 'confirmed'