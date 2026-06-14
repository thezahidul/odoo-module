from odoo import models, fields, api


class FestivalBonusWizard(models.TransientModel):
    _name = "festival.bonus.wizard"
    _description = "Bulk Add Employees to Festival Bonus"

    bonus_id = fields.Many2one(
        "festival.bonus.config", string="Bonus Config", required=True
    )
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employees",
        domain=[("active", "=", True)],
    )
    department_id = fields.Many2one("hr.department", string="Filter by Department")

    # gender → sex (Odoo 19)
    sex = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        string="Filter by Gender",
    )

    religion = fields.Selection(
        [
            ("islam", "Islam"),
            ("hinduism", "Hinduism"),
            ("christianity", "Christianity"),
            ("buddhism", "Buddhism"),
            ("other", "Other"),
        ],
        string="Filter by Religion",
    )

    def _get_employee_domain(self):
        domain = [("active", "=", True)]
        if self.department_id:
            domain.append(("department_id", "=", self.department_id.id))
        if self.sex:
            domain.append(("sex", "=", self.sex))  # sex field
        if self.religion:
            domain.append(("religion", "=", self.religion))
        return domain

    @api.onchange("department_id", "sex", "religion")
    def _onchange_filters(self):
        if self.department_id or self.sex or self.religion:
            self.employee_ids = self.env["hr.employee"].search(
                self._get_employee_domain()
            )
        else:
            self.employee_ids = False

    def action_add_employees(self):
        self.ensure_one()
        bonus = self.bonus_id
        existing_employee_ids = bonus.bonus_line_ids.mapped("employee_id").ids

        lines_to_create = []
        for employee in self.employee_ids:
            if employee.id in existing_employee_ids:
                continue
            salary = self.env["festival.bonus.line"]._get_salary_from_payslip(
                employee,
                bonus.salary_base,
            )
            lines_to_create.append(
                {
                    "bonus_id": bonus.id,
                    "employee_id": employee.id,
                    "joining_date": employee.contract_date_start or False,
                    "salary_base_amount": salary,
                }
            )

        if lines_to_create:
            self.env["festival.bonus.line"].create(lines_to_create)

        return {"type": "ir.actions.act_window_close"}
