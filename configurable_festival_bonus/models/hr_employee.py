from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    religion = fields.Selection(
        [
            ("islam", "Islam"),
            ("hinduism", "Hinduism"),
            ("christianity", "Christianity"),
            ("buddhism", "Buddhism"),
            ("other", "Other"),
        ],
        string="Religion",
        tracking=True,
        groups="hr.group_hr_user",
    )

    bonus_line_ids = fields.One2many(
        "festival.bonus.line",
        "employee_id",
        string="Bonus Records",
    )
    bonus_count = fields.Integer(
        string="Bonus Count",
        compute="_compute_bonus_count",
        store=True,
    )

    @api.depends("bonus_line_ids")
    def _compute_bonus_count(self):
        groups = self.env["festival.bonus.line"]._read_group(
            domain=[("employee_id", "in", self.ids)],
            groupby=["employee_id"],
            aggregates=["__count"],
        )
        count_map = {employee.id: count for employee, count in groups}
        for employee in self:
            employee.bonus_count = count_map.get(employee.id, 0)

    def action_open_festival_bonus(self):
        self.ensure_one()
        return {
            "name": _("Festival Bonus Records"),
            "type": "ir.actions.act_window",
            "res_model": "festival.bonus.line",
            "view_mode": "list,form",
            "domain": [("employee_id", "=", self.id)],
            "context": {"default_employee_id": self.id},
            "target": "current",
        }
