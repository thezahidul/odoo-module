from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class KpiTemplateLine(models.Model):
    _name = 'kpi.template.line'
    _description = 'KPI Template Line'
    _rec_name = 'skill_name'

    template_id = fields.Many2one('kpi.template', string="Template", ondelete='cascade')
    skill_type = fields.Selection([
        ('hard', 'Hard Skill'),
        ('soft', 'Soft Skill'),
        ('growth', 'Growth Skill')
    ], string="Skill Type", required=True)
    skill_name = fields.Char(string="Skill Name", required=True)
    weight = fields.Float(string="Weight (%)", default=0.0)
    