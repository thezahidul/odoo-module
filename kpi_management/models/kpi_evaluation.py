from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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

    department_id = fields.Many2one(
        'hr.department', 
        string="Department", 
        related='employee_id.department_id', 
        store=True, 
        readonly=True
    )

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._check_duplicate_evaluation(vals)
        return super().create(vals_list)

    def write(self, vals):
        for record in self:
            check_vals = {field: vals.get(field, getattr(record, field)) 
                          for field in ['employee_id', 'template_id', 'evaluation_date']}
            self._check_duplicate_evaluation(check_vals, exclude_id=record.id)
        return super().write(vals)

    def _check_duplicate_evaluation(self, vals, exclude_id=None):
        domain = [
            ('employee_id', '=', vals.get('employee_id')),
            ('template_id', '=', vals.get('template_id')),
            ('evaluation_date', '=', vals.get('evaluation_date')),
        ]
        if exclude_id:
            domain.append(('id', '!=', exclude_id))
            
        if self.search_count(domain) > 0:
            raise ValidationError(_("This template has already been evaluated for this employee on this date."))

    @api.depends('line_ids.skill_id')
    def _compute_evaluation_skills(self):
        for record in self:
            record.evaluation_skill_ids = record.line_ids.mapped('skill_id')

    @api.onchange('template_id')
    def _onchange_template_id(self):
        if self.template_id:
            self.line_ids = [(5, 0, 0)]
            
            # Copying data from template lines
            new_lines = []
            for line in self.template_id.line_ids:
                new_lines.append((0, 0, {
                    'skill_id': line.skill_id.id,
                    'achieved_score': 0.0,
                }))
            self.line_ids = new_lines
