from odoo import models, fields, api, _

class HrJob(models.Model):
    _inherit = 'hr.job'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('first_stage', '1st Stage'),
        ('second_stage', '2nd Stage'),
        ('final_stage', 'Final Stage'),
        ('open', 'Recruitment In Progress'),
        ('refused', 'Refused'),
    ], string='Status', readonly=True, default='draft', tracking=True)

    # Approver fields with Bangla Labels as requested
    approver_stage_1 = fields.Many2one('res.users', string='1st stage Approvl')
    approver_stage_2 = fields.Many2one('res.users', string='2nd stage Approval')
    approver_final = fields.Many2one('res.users', string='3rd stage Approval')

    def action_submit_first(self):
        self.write({'state': 'first_stage'})

    def action_approve_second(self):
        self.write({'state': 'second_stage'})

    def action_approve_final(self):
        self.write({'state': 'final_stage'})

    def action_set_to_open(self):
        """Final stage approval will automatically publish the job post"""
        self.write({
            'state': 'open',
            'website_published': True  # This makes it live on the website
        })
        
    def action_refuse(self):
        self.write({'state': 'refused'})