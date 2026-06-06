from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'name' in vals and self.search([('name', '=', vals['name'])]):
                raise ValidationError(_("This skill name already exists!"))
        return super().create(vals_list)

    def write(self, vals):
        if 'name' in vals:
            for record in self:
                if self.search([('name', '=', vals['name']), ('id', '!=', record.id)]):
                    raise ValidationError(_("This skill name already exists!"))
        return super().write(vals)

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