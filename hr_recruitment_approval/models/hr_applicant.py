from odoo import models, api

class HrApplicant(models.Model):
    _inherit='hr.applicant'

    def action_generate_offer_letter_pdf(self):
        return self.env.ref('hr_recruitment_approval.action_report_offer_letter').report_action(self)
    
    def action_send_offer_email(self):
        template = self.env.ref('hr_recruitment_approval.email_template_offer_letter', False)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': {
                'default_model': 'hr.applicant',
                'default_res_ids': [self.id], 
                'default_template_id': template.id if template else False,
                'default_composition_mode': 'comment',
            }
        }
