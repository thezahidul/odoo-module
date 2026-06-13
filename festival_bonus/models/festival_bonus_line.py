from odoo import models, fields, api
from dateutil.relativedelta import relativedelta


class FestivalBonusLine(models.Model):
    _name = "festival.bonus.line"
    _description = "Festival Bonus Lines"
    _rec_name = "employee_id"

    bonus_id = fields.Many2one(
        "festival.bonus.config",
        ondelete="cascade",
        string="Bonus Configuration",
        index=True,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=True,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="bonus_id.company_id.currency_id",
        store=True,
    )
    joining_date = fields.Date(string="Joining Date")
    basic_salary = fields.Monetary(string="Basic Salary", currency_field="currency_id")

    # Computed fields
    service_months = fields.Integer(
        string="Service (Months)",
        compute="_compute_eligibility",
        store=True,
    )
    is_eligible = fields.Boolean(
        string="Eligible",
        compute="_compute_eligibility",
        store=True,
    )
    eligibility_status = fields.Char(
        string="Status",
        compute="_compute_eligibility",
        store=True,
    )
    bonus_amount = fields.Monetary(
        string="Bonus Amount",
        currency_field="currency_id",
        compute="_compute_bonus_amount",
        store=True,
    )

    @api.depends(
        "joining_date",
        "bonus_id.bonus_month",
        "bonus_id.bonus_year",
        "bonus_id.min_service_months",
    )
    def _get_salary_from_payslip(self, employee, bonus_id):
        """Most recent confirmed payslip থেকে selected salary field নাও"""
        if not employee or not bonus_id.salary_base:
            return 0.0

        # hr.payslip model available আছে কিনা check
        if "hr.payslip" not in self.env:
            return employee.wage or 0.0

        payslip = self.env["hr.payslip"].search(
            [
                ("employee_id", "=", employee.id),
                ("state", "in", ["done", "paid"]),
            ],
            order="date_to desc",
            limit=1,
        )

        if payslip:
            return getattr(payslip, bonus_id.salary_base, 0.0) or 0.0

        # Payslip না থাকলে employee wage fallback
        return employee.wage or 0.0

    def _compute_eligibility(self):
        for line in self:
            if (
                not line.joining_date
                or not line.bonus_id.bonus_month
                or not line.bonus_id.bonus_year
            ):
                line.service_months = 0
                line.is_eligible = False
                line.eligibility_status = "No joining date"
                continue

            bonus_date = fields.Date.from_string(
                f"{line.bonus_id.bonus_year}-{int(line.bonus_id.bonus_month):02d}-01"
            )

            delta = relativedelta(bonus_date, line.joining_date)
            months = delta.years * 12 + delta.months

            line.service_months = max(months, 0)
            line.is_eligible = months >= (line.bonus_id.min_service_months or 0)
            line.eligibility_status = (
                "✔ Eligible"
                if line.is_eligible
                else f"✘ Need {(line.bonus_id.min_service_months or 0) - months} more month(s)"
            )

    @api.depends("basic_salary", "bonus_id.bonus_percentage", "is_eligible")
    def _compute_bonus_amount(self):
        for line in self:
            if (
                line.is_eligible
                and line.basic_salary
                and line.bonus_id.bonus_percentage
            ):
                line.bonus_amount = (
                    line.basic_salary * line.bonus_id.bonus_percentage / 100
                )
            else:
                line.bonus_amount = 0.0

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        employee = self.employee_id
        self.joining_date = employee.contract_date_start or False
        self.basic_salary = self._get_salary_from_payslip(employee, self.bonus_id)
        self._compute_eligibility()
        self._compute_bonus_amount()
