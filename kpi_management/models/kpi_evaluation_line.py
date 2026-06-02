from odoo import models, fields, api

class KpiEvaluationLine(models.Model):
    _name = 'kpi.evaluation.line'
    _description = 'KPI Evaluation Line'
    _rec_name='skill_line_id'

    evaluation_id = fields.Many2one('kpi.evaluation', string="Evaluation")
    skill_line_id = fields.Many2one('kpi.template.line', string="Skill")
    achieved_score = fields.Float(string="Achieved Score (0-100)")