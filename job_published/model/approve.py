from odoo import models, fields, api

class Job(models.Model):
    _inherit = 'hr.job'
    _name = 'hr.job'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('pm_approved', 'PM Approved'),
        ('hr_approved', 'HR Approved'),
        ('published', 'Published')
    ], string='Status', default='draft', readonly=True, copy=False)

    def action_pm_approve(self):
        self.state = 'pm_approved'
        
    def action_hr_approve(self):
        self.state = 'hr_approved'

    def action_ceo_approve(self):
        self.state = 'published'
        if hasattr(self, 'is_published'):
            self.is_published = True