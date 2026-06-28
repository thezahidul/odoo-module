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
    job_id = fields.Many2one(
        "hr.job",
        string="Job Position",
        related="employee_id.job_id",
        store=True,
        readonly=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="bonus_id.company_id.currency_id",
        store=True,
    )
    joining_date = fields.Date(string="Joining Date")
    salary_base_amount = fields.Monetary(
        string="Salary Amount",
        currency_field="currency_id",
    )

    # Eligibility (computed from joining_date -> bonus date)
    service_months = fields.Integer(
        string="Service (Months)",
        compute="_compute_eligibility",
        store=True,
    )
    service_days = fields.Integer(
        string="Service (Days)",
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

    # Bonus result
    applied_percentage = fields.Float(
        string="Applied %",
        digits=(5, 2),
        compute="_compute_bonus_amount",
        store=True,
        help="The bonus percentage actually applied to this employee "
        "(from designation-wise rate or the template default).",
    )
    bonus_amount = fields.Monetary(
        string="Bonus Amount",
        currency_field="currency_id",
        compute="_compute_bonus_amount",
        store=True,
    )
    is_clamped = fields.Boolean(
        string="Amount Adjusted",
        compute="_compute_bonus_amount",
        store=True,
        help="True if the min/max limit was applied instead of the raw percentage calculation.",
    )

    def _get_salary_from_payslip(self, employee, salary_base):
        if not employee:
            return 0.0
        if "hr.payslip" in self.env:
            payslip = self.env["hr.payslip"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("state", "in", ["done", "paid"]),
                ],
                order="date_to desc",
                limit=1,
            )
            if payslip and salary_base:
                return getattr(payslip, salary_base, 0.0) or 0.0
        return employee.wage or 0.0

    def _get_bonus_reference_date(self):
        self.ensure_one()
        return self.bonus_id.bonus_date

    @api.depends(
        "joining_date",
        "bonus_id.bonus_date",
        "bonus_id.calculation_basis",
        "bonus_id.min_service_months",
        "bonus_id.min_service_days",
    )
    def _compute_eligibility(self):
        """
        Joining date theke bonus_date porjonto:
        - service_months: relativedelta diye month count (info hisebe sob somoy compute hoy)
        - service_days: actual calendar day count (info hisebe sob somoy compute hoy)

        Eligibility check template'r calculation_basis onujayi hoy:
        - 'month' hole  -> service_months >= min_service_months
        - 'day' hole    -> service_days >= min_service_days
        """
        for line in self:
            bonus_date = line._get_bonus_reference_date()
            if not line.joining_date or not bonus_date:
                line.service_months = 0
                line.service_days = 0
                line.is_eligible = False
                line.eligibility_status = "No joining date"
                continue

            delta = relativedelta(bonus_date, line.joining_date)
            months = delta.years * 12 + delta.months
            days = (bonus_date - line.joining_date).days

            line.service_months = max(months, 0)
            line.service_days = max(days, 0)

            basis = line.bonus_id.calculation_basis

            if basis == "day":
                required_days = line.bonus_id.min_service_days or 0
                line.is_eligible = days >= required_days
                line.eligibility_status = (
                    "✔ Eligible"
                    if line.is_eligible
                    else f"✘ Need {required_days - days} more day(s)"
                )
            else:
                required_months = line.bonus_id.min_service_months or 0
                line.is_eligible = months >= required_months
                line.eligibility_status = (
                    "✔ Eligible"
                    if line.is_eligible
                    else f"✘ Need {required_months - months} more month(s)"
                )

    @api.depends(
        "salary_base_amount",
        "is_eligible",
        "service_days",
        "employee_id.job_id",
        "bonus_id.bonus_percentage",
        "bonus_id.calculation_basis",
        "bonus_id.min_amount",
        "bonus_id.max_amount",
        "bonus_id.use_designation_rates",
        "bonus_id.designation_rate_ids.bonus_percentage",
        "bonus_id.designation_rate_ids.job_id",
    )
    def _compute_bonus_amount(self):
        for line in self:
            config = line.bonus_id
            percentage = (
                config.get_percentage_for_employee(line.employee_id) if config else 0.0
            )
            line.applied_percentage = percentage

            if not line.is_eligible or not line.salary_base_amount or not percentage:
                line.bonus_amount = 0.0
                line.is_clamped = False
                continue

            # Step 1: Calculate raw amount per calculation_basis
            if config.calculation_basis == "day":
                # Day basis: per-day salary x eligible days x percentage
                per_day_salary = line.salary_base_amount / 30.0
                calculated = per_day_salary * line.service_days * percentage / 100
            else:
                # Month basis: full salary x percentage
                calculated = line.salary_base_amount * percentage / 100

            # Step 2: Clamp between min_amount and max_amount
            final_amount = calculated
            clamped = False

            if config.min_amount and calculated < config.min_amount:
                final_amount = config.min_amount
                clamped = True
            elif config.max_amount and calculated > config.max_amount:
                final_amount = config.max_amount
                clamped = True

            line.bonus_amount = final_amount
            line.is_clamped = clamped

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        employee = self.employee_id
        self.joining_date = employee.contract_date_start or False
        self.salary_base_amount = self._get_salary_from_payslip(
            employee,
            self.bonus_id.salary_base,
        )
        self._compute_eligibility()
        self._compute_bonus_amount()
