from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    @api.constrains('name', 'company_id')
    def _check_unique_name_company(self):
        for record in self:
            domain = [
                ('name', '=', record.name),
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ]
            if self.env['hr.department'].search_count(domain) > 0:
                raise ValidationError(_("A department with this name already exists in this company, regardless of the parent department!"))