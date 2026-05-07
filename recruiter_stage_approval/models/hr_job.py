from odoo import models, fields, api, _
from odoo.exceptions import UserError

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

    approver_stage_1 = fields.Many2one('res.users', string='1st Stage Approver', required=True)
    approver_stage_2 = fields.Many2one('res.users', string='2nd Stage Approver', required=True)
    approver_final = fields.Many2one('res.users', string='Final Approver', required=True)

    is_final_approver = fields.Boolean(compute='_compute_is_final_approver')

    @api.depends('approver_final')
    def _compute_is_final_approver(self):
        for record in self:
            # Check if the current user is the designated Final Approver
            record.is_final_approver = (self.env.user == record.approver_final)

    def action_submit_first(self):
        self.write({'state': 'first_stage'})

    def action_approve_second(self):
        for record in self:
            if self.env.user != record.approver_stage_1:
                raise UserError(_("Only the First Stage Approver (%s) is authorized to approve this stage.") % record.approver_stage_1.name)
            record.write({'state': 'second_stage'})

    def action_approve_final(self):
        for record in self:
            if self.env.user != record.approver_stage_2:
                raise UserError(_("Only the Second Stage Approver (%s) is authorized to approve this stage.") % record.approver_stage_2.name)
            record.write({'state': 'final_stage'})

    def action_set_to_open(self):
        for record in self:
            if self.env.user != record.approver_final:
                raise UserError(_("Only the Final Approver (%s) is authorized to publish this job.") % record.approver_final.name)
            record.write({
                'state': 'open',
                'website_published': True
            })
        
    def action_refuse(self):
        for record in self:
            if self.env.user != record.approver_final:
                raise UserError(_("Only the Final Approver (%s) is authorized to refuse this request.") % record.approver_final.name)
            
            if record.state != 'final_stage':
                raise UserError(_("Refusal is only permitted during the Final Stage."))
                
            record.write({'state': 'refused'})

            