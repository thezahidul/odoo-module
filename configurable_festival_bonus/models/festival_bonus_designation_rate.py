from odoo import models, fields, api


class FestivalBonusDesignationRate(models.Model):
    _name = "festival.bonus.designation.rate"
    _description = "Festival Bonus Designation-wise Rate"
    _order = "sequence, id"

    template_id = fields.Many2one(
        "festival.bonus.template",
        ondelete="cascade",
        string="Template",
        index=True,
    )
    config_id = fields.Many2one(
        "festival.bonus.config",
        ondelete="cascade",
        string="Festival Bonus",
        index=True,
    )
    sequence = fields.Integer(string="Sequence", default=10)

    job_id = fields.Many2one(
        "hr.job",
        string="Designation",
        required=True,
        help="Employees with this job position will get the percentage below "
        "instead of the template's default percentage.",
    )
    bonus_percentage = fields.Float(
        string="Bonus Percentage (%)",
        digits=(5, 2),
        required=True,
    )

    company_id = fields.Many2one("res.company", string="Company")
    department_id = fields.Many2one("hr.department", string="Department")
    job_id = fields.Many2one("hr.job", string="Designation")
    designation_id = fields.Many2one("hr.job", string="Designation")

    def name_get(self):
        result = []
        for rec in self:
            label = f"{rec.job_id.name} — {rec.bonus_percentage}%"
            result.append((rec.id, label))
        return result
