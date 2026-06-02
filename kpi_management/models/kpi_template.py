from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class KpiTemplate(models.Model):
    _name = "kpi.template"
    _description = "KPI Template"

    name = fields.Char(string="Template Name", required=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    department_id = fields.Many2one("hr.department", string="Department", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
        default="draft",
        string="Status",
    )

    line_ids = fields.One2many("kpi.template.line", "template_id", string="Skills")

    _sql_constraints = [
        ("unique_active_template", "CHECK(1=1)", "Logic handled by constraint method"),
    ]

    @api.constrains("state", "department_id")
    def _check_unique_active_template(self):
        for record in self:
            if record.state == "active":
                existing = self.search(
                    [
                        ("department_id", "=", record.department_id.id),
                        ("state", "=", "active"),
                        ("id", "!=", record.id),
                    ]
                )
                if existing:
                    raise ValidationError(
                        _("Only one active KPI template is allowed per department!")
                    )

    def action_activate(self):
        # অন্যান্য ডিপার্টমেন্টের টেমপ্লেট আর্কিভ করে ফেলা (অপশনাল)
        self.state = 'active'

    def action_archive(self):
        self.state = 'archived'