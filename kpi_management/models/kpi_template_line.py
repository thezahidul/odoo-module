from odoo import models, fields, api

class KpiTemplateLine(models.Model):
    _name = 'kpi.template.line'
    _description = 'KPI Template Line'
    _rec_name = 'skill_id'


    template_id = fields.Many2one('kpi.template', string="Template", ondelete='cascade', required=True)
    skill_id = fields.Many2one('kpi.skill.library', string="Skill", required=True)
    skill_type = fields.Selection(related='skill_id.skill_type', string="Skill Type", store=True)
    weight = fields.Float(string="Weight (%)", default=0.0, required=True)

    @api.onchange('skill_id')
    def _onchange_skill_id(self):
        # Whenever the user selects a skill, automatic typing will occur.
        if self.skill_id:
            self.skill_type = self.skill_id.skill_type