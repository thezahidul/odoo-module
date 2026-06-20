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
    job_id = fields.Many2one("hr.job", string="Filter by Designation")
    company_id = fields.Many2one("res.company", string="Filter by Company")
    employee_type = fields.Selection(
        [
            ("employee", "Employee"),
            ("student", "Student"),
            ("freelance", "Freelancer"),
        ],
        string="Filter by Employee Type",
    )
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
        if self.job_id:
            domain.append(("job_id", "=", self.job_id.id))
        if self.company_id:
            domain.append(("company_id", "=", self.company_id.id))
        if self.employee_type:
            domain.append(("employee_type", "=", self.employee_type))
        if self.sex:
            domain.append(("sex", "=", self.sex))
        if self.religion:
            domain.append(("religion", "=", self.religion))
        return domain

    @api.onchange(
        "department_id", "job_id", "company_id", "employee_type", "sex", "religion"
    )
    def _onchange_filters(self):
        has_filter = any(
            [
                self.department_id,
                self.job_id,
                self.company_id,
                self.employee_type,
                self.sex,
                self.religion,
            ]
        )
        if has_filter:
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
