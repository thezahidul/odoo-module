from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class KpiTemplate(models.Model):
    _name = "kpi.template"
    _description = "KPI Template"
    _inherit=['mail.thread']

    name = fields.Char(string="Template Name", required=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    department_id = fields.Many2one("hr.department", string="Department", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("archived", "Archived")],
        default="draft",
        string="Status",
        copy=False,
        tracking=True,
    )

    line_ids = fields.One2many("kpi.template.line", "template_id", string="Skills")

    selected_skill_ids = fields.Many2many('kpi.skill.library', compute='_compute_selected_skills')

    create_date = fields.Datetime(string="Created Date", readonly=True)
    activated_date = fields.Datetime(string="Activated Date", readonly=True)
    archived_date = fields.Datetime(string="Archived Date", readonly=True)

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company, required=True
    )

    # SQL Constraints are for data integrity at DB level. 
    # Since active status is conditional, we use Python constraints.
    _sql_constraints = [
        ("name_company_unique", "UNIQUE(name, company_id)", "Template name must be unique per company!")
    ]
    
    

    @api.depends('line_ids.skill_id')
    def _compute_selected_skills(self):
        for record in self:
            record.selected_skill_ids = record.line_ids.mapped('skill_id')

    @api.constrains("state", "department_id")
    def _check_unique_active_template(self):
        for record in self:
            if record.state == "active":
                existing = self.search_count([
                    ("department_id", "=", record.department_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", record.id),
                ])
                if existing > 0:
                    raise ValidationError(
                        _("Only one active KPI template is allowed per department!")
                    )

    def action_activate(self):
        now = fields.Datetime.now()
        
        # Date when archiving previous ones
        previous_active = self.search([
            ("department_id", "=", self.department_id.id),
            ("state", "=", "active"),
            ("id", "!=", self.id)
        ])
        if previous_active:
            previous_active.write({
                'state': 'archived',
                'archived_date': now
            })
            
        # Date given when activating the current one
        self.write({
            'state': 'active',
            'activated_date': now
        })

    def action_archive(self):
        self.write({
            'state': 'archived',
            'archived_date': fields.Datetime.now()
        })