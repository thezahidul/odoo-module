# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrGratuitySettlementWizard(models.TransientModel):
    """
    Wizard to generate and batch print Gratuity Settlement Reports.
    Allows HR managers to print compiled reports for multiple employees simultaneously.
    """
    _name = 'hr.gratuity.settlement.wizard'
    _description = 'Gratuity Settlement Report Wizard'

    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Employees',
        required=True,
        help="Select the corporate employees to filter the batch printing."
    )

    report_date = fields.Date(
        string='Report Generation Date',
        default=fields.Date.today,
        required=True,
    )

    state_filter = fields.Selection(
        selection=[
            ('all', 'All States'),
            ('approved', 'Approved Only'),
            ('paid', 'Fully Paid Only'),
        ],
        string='Status Filter',
        default='all',
        required=True,
        help="Filter records by their current workflow lifecycle state."
    )

    def action_print_report(self):
        """
        Processes selected parameters, queries database, and routes target 
        accrual records into the synchronized batch A4 PDF report print queue.
        """
        self.ensure_one()
        
        # Build dynamic search payload based on wizard user parameters
        domain = [('employee_id', 'in', self.employee_ids.ids)]
        if self.state_filter != 'all':
            domain.append(('state', '=', self.state_filter))

        # Core query resolution execution
        records = self.env['hr.gratuity'].search(domain)
        if not records:
            raise UserError(_('No active Gratuity records matching your selected filters were found in the database.'))

        return self.env.ref(
            'hr_gratuity.action_report_gratuity_settlement'
        ).report_action(records)