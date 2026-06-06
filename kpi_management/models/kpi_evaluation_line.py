from odoo import models, fields, api
from odoo.exceptions import ValidationError

class KpiEvaluationLine(models.Model):
    _name = 'kpi.evaluation.line'
    _description = 'KPI Evaluation Line'
    _rec_name = 'skill_id'

    evaluation_id = fields.Many2one('kpi.evaluation', string="Evaluation", ondelete='cascade')
    skill_id = fields.Many2one('kpi.skill.library', string="Skill", required=True)
    achieved_score = fields.Float(string="Achieved Score (0-100)")

    @api.constrains('name', 'company_id')
    def _check_unique_name_company(self):
        for record in self:
            duplicates = self.env['kpi.template'].search([
                ('name', '=', record.name),
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ])
            if duplicates:
                raise ValidationError("A template with this name already exists for this company!")
            
    @api.constrains('achieved_score')
    def _check_score_range(self):
        for line in self:
            if line.achieved_score < 0 or line.achieved_score > 100:
                raise ValidationError("The score must be between 0 and 100.")