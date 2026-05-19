# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrGratuitySettlementWizard(models.TransientModel):
    """
    Gratuity Settlement Report তৈরি করার Wizard।
    একাধিক কর্মচারীর রিপোর্ট একসাথে বের করা যাবে।
    """
    _name = 'hr.gratuity.settlement.wizard'
    _description = 'Gratuity Settlement Report Wizard'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='কর্মচারী',
        required=True,
    )

    report_date = fields.Date(
        string='রিপোর্টের তারিখ',
        default=fields.Date.today,
    )

    state_filter = fields.Selection(
        selection=[
            ('all', 'সব অবস্থা'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
        ],
        string='অবস্থা ফিল্টার',
        default='all',
    )

    def action_print_report(self):
        self.ensure_one()
        domain = [('employee_id', 'in', self.employee_ids.ids)]
        if self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))

        records = self.env['hr.gratuity'].search(domain)
        if not records:
            raise UserError(_('নির্বাচিত কর্মচারীদের কোনো Gratuity রেকর্ড পাওয়া যায়নি।'))

        return self.env.ref(
            'hr_gratuity_bd.action_report_gratuity_settlement'
        ).report_action(records)
