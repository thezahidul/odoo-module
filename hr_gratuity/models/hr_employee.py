# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrEmployee(models.Model):
    """
    Extends the hr.employee model to add a Gratuity Smart Button.
    Gratuity data is stored separately in the hr.gratuity model.
    """
    _inherit = 'hr.employee'

    gratuity_ids = fields.One2many(
        comodel_name='hr.gratuity',
        inverse_name='employee_id',
        string='Gratuity Records',
    )

    gratuity_count = fields.Integer(
        string='Gratuity Count',
        compute='_compute_gratuity_count',
    )

    gratuity_state = fields.Selection(
        selection=[
            ('none', 'No Record'),
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
        ],
        string='Gratuity Status',
        compute='_compute_gratuity_count',
    )

    @api.depends('gratuity_ids', 'gratuity_ids.state')
    def _compute_gratuity_count(self):
        for employee in self:
            # Filter out cancelled records from the count and state check
            records = employee.gratuity_ids.filtered(
                lambda r: r.state != 'cancel'  # ওডু-র স্ট্যান্ডার্ড 'cancel' স্টেট সাধারণত 'cancelled' এর চেয়ে বেশি ব্যবহৃত হয়, আপনার মডেলে যা আছে তা মিলিয়ে নেবেন
            )
            employee.gratuity_count = len(records)
            
            if not records:
                employee.gratuity_state = 'none'
            else:
                # Fetch the status of the most recently created record
                latest = records.sorted('create_date', reverse=True)[0]
                employee.gratuity_state = latest.state

    def action_open_gratuity(self):
        """Action to open Gratuity records directly from the Employee Form"""
        self.ensure_one()
        
        # ওডু ১৯ স্ট্যান্ডার্ড ডাইনামিক অ্যাকশন রিটার্ন (নতুন মডিউল নেম স্পেস সহ)
        action = {
            'name': 'Gratuity Settlement',
            'type': 'ir.actions.act_window',
            'res_model': 'hr.gratuity',
            'view_mode': 'list,form',
            'domain': [('employee_id', '=', self.id)],
            'context': {
                'default_employee_id': self.id,
                'default_joining_date': self.date_start,
            },
            'target': 'current',
        }
        
        # If there is exactly one record, open its form view directly for better UX
        active_records = self.gratuity_ids.filtered(lambda r: r.state != 'cancel')
        if len(active_records) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = active_records[0].id
            
        return action