from odoo import models, fields

class KpiSkillLibrary(models.Model):
    _name = "kpi.skill.library"
    _description = "KPI Skill Library"

    name = fields.Char(string="Skill Name", required=True)
    skill_type = fields.Selection([
        ('hard', 'Hard Skill'),
        ('soft', 'Soft Skill'),
        ('growth', 'Growth Skill')
    ], string="Skill Type", required=True)

    _sql_constraints = [
        ('unique_skill_name', 'unique(name)', 'This skill name already exists!')
    ]