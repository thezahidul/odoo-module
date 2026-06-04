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

    active = fields.Boolean(string="Active", default=True)

    _sql_constraints = [
        ('unique_skill_name', 'unique(name)', 'This skill name already exists!')
    ]

    def unlink(self):
        # Checking whether the skill has been used elsewhere (such as in the template line or evaluation line)
        used_in_template = self.env['kpi.template.line'].search([('skill_id', 'in', self.ids)])
        used_in_evaluation = self.env['kpi.evaluation.line'].search([('skill_id', 'in', self.ids)])
        
        if used_in_template or used_in_evaluation:
            # If used, just archive it instead of deleting it.
            self.write({'active': False})
            return True
        
        # If it is not used anywhere, then let it be deleted.
        return super(KpiSkillLibrary, self).unlink()