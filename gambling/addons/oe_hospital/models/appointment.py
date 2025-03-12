# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HospitalAppointment(models.Model):
    _name = "hospital.appointment"
    _inherit = ['mail.thread']
    _description = "Hospital Appointment"
    _rec_names_search = ['reference', 'patient_id']
    _rec_name = "patient_id"

    reference = fields.Char(string='Reference', default='New', tracking=True)
    patient_id = fields.Many2one(
        'hospital.patient', required=True, ondelete='restrict'
    )
    date_appointment = fields.Date(string='Date', tracking=True)
    note = fields.Html()
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('ongoing', 'Ongoing'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
        ], string="Status", default='draft', tracking=True
    )
    appointment_line_ids = fields.One2many(
        'hospital.appointment.line',
        'appointment_id',
        string='Appointment Lines', ondelete='restrict'
    )
    total_qty = fields.Float(compute="_compute_total_qty", store=True)
    date_of_birth = fields.Date(related='patient_id.date_of_birth', store=True)

    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code(
                'hospital.appointment'
            )
        return super().create(vals)

    @api.depends('appointment_line_ids.qty')
    def _compute_total_qty(self):
        for rec in self:
            rec.total_qty = sum(rec.appointment_line_ids.mapped('qty'))

    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.reference}] {rec.patient_id.name}"

    def action_confirm(self):
        for rec in self:
            rec.state = 'confirmed'

    def action_ongoing(self):
        for rec in self:
            rec.state = 'ongoing'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'


class HospitalAppointmentLine(models.Model):
    _name = "hospital.appointment.line"
    _description = "Hospital Appointment Line"

    appointment_id = fields.Many2one(
        'hospital.appointment', string='Appointment'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    qty = fields.Float(string='Quantity')
