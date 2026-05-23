from odoo import models, fields, api

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def action_generate_offer_letter(self):
        # রিপোর্টে আপনার রিপোর্ট XML আইডি দিন
        return self.env.ref('your_module_name.action_report_offer_letter').report_action(self)

    def action_send_offer_email(self):
        self.ensure_one()
        template = self.env.ref('your_module_name.email_template_offer_letter', False)
        if template:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'mail.compose.message',
                'target': 'new',
                'context': {
                    'default_model': 'hr.applicant',
                    'default_res_id': self.id,
                    'default_template_id': template.id,
                    'default_composition_mode': 'comment',
                },
            }