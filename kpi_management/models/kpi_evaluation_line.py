from odoo import models, fields, api
from odoo.exceptions import ValidationError

class KpiEvaluationLine(models.Model):
    _name = 'kpi.evaluation.line'
    _description = 'KPI Evaluation Line'
    _rec_name='skill_line_id'

    evaluation_id = fields.Many2one('kpi.evaluation', string="Evaluation")
    skill_line_id = fields.Many2one('kpi.template.line', string="Skill")
    achieved_score = fields.Float(string="Achieved Score (0-100)")

    @api.constrains('skill_line_id', 'evaluation_id')

    def _check_unique_skill(self):
        for line in self:
            # Check if the same skill line is present twice in the same evaluation.
            count = self.env['kpi.evaluation.line'].search_count([
                ('evaluation_id', '=', line.evaluation_id.id),
                ('skill_line_id', '=', line.skill_line_id.id)
            ])
            if count > 1:
                raise ValidationError("This skill has already been added. Please delete the duplicate entry.")
            
    @api.constrains('achieved_score')
    def _check_score_range(self):
        for line in self:
            if line.achieved_score < 0 or line.achieved_score > 100:
                raise ValidationError("The score must be between 0 and 100.")