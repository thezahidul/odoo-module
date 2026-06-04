from odoo import models, fields, api


class KpiEvaluation(models.Model):
    _name = "kpi.evaluation"
    _description = "KPI Evaluation"
    _rec_name = "employee_id"

    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    template_id = fields.Many2one(
        "kpi.template",
        string="KPI Template",
        domain=[("state", "=", "active")],
        required=True,
    )
    evaluation_date = fields.Date(
        string="Evaluation Date", default=fields.Date.context_today
    )
    line_ids = fields.One2many(
        "kpi.evaluation.line", "evaluation_id", string="Score Details"
    )
    total_score = fields.Float(
        string="Total Score", compute="_compute_total_score", store=True
    )

    evaluation_skill_ids = fields.Many2many('kpi.skill.library', compute='_compute_evaluation_skills')

    @api.depends('line_ids.achieved_score', 'line_ids.skill_id')
    def _compute_total_score(self):
        for record in self:
            total = 0.0
            for line in record.line_ids:
                template_line = record.template_id.line_ids.filtered(
                    lambda l: l.skill_id == line.skill_id
                )
                weight = template_line.weight if template_line else 0.0
                total += line.achieved_score * (weight / 100)
            
            record.total_score = total

    _sql_constraints = [
        (
            "unique_evaluation",
            "unique(employee_id, template_id, evaluation_date)",
            "This template has already been evaluated for this employee on this date.",
        )
    ]

    @api.depends('line_ids.skill_id')
    def _compute_evaluation_skills(self):
        for record in self:
            record.evaluation_skill_ids = record.line_ids.mapped('skill_id')
