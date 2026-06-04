from odoo import models, fields, api
from odoo.exceptions import ValidationError

class KpiEvaluationLine(models.Model):
    _name = 'kpi.evaluation.line'
    _description = 'KPI Evaluation Line'
    _rec_name = 'skill_id'

    evaluation_id = fields.Many2one('kpi.evaluation', string="Evaluation", ondelete='cascade')
    skill_id = fields.Many2one('kpi.skill.library', string="Skill", required=True)
    achieved_score = fields.Float(string="Achieved Score (0-100)")

    @api.constrains('skill_id', 'evaluation_id')
    def _check_unique_skill(self):
        for line in self:
            # Checking if the current evaluation has the same skill or not
            count = self.env['kpi.evaluation.line'].search_count([
                ('evaluation_id', '=', line.evaluation_id.id),
                ('skill_id', '=', line.skill_id.id),
                ('id', '!=', line.id)
            ])
            if count > 0:
                raise ValidationError("This skill has already been added. Please remove the duplicate entry.")
            
    @api.constrains('achieved_score')
    def _check_score_range(self):
        for line in self:
            if line.achieved_score < 0 or line.achieved_score > 100:
                raise ValidationError("The score must be between 0 and 100.")