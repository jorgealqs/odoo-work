# -*- coding: utf-8 -*-

from odoo import models, fields, _, api
from odoo.exceptions import ValidationError  # type: ignore
import logging

_logger = logging.getLogger(__name__)


class HospitalPatient(models.Model):
    _name = 'hospital.patient'
    _inherit = ['mail.thread']
    _description = 'Hospital Patient'

    name = fields.Char(
        string='Name', required=True, tracking=True
    )
    date_of_birth = fields.Date(string='Date of Birth', tracking=True)
    gender = fields.Selection(
        [
            ('male', 'male'),
            ('female', 'female')
        ], string="Gender", tracking=True
    )
    tag_ids = fields.Many2many(
        'hospital.patient.tag', string='Tags'
    )

    @api.ondelete(at_uninstall=False)
    def unlink(self):
        for rec in self:
            domain = [('patient_id', '=', rec.id)]
            appointments = self.env['hospital.appointment'].search(domain)
            if appointments:
                raise ValidationError(
                    _(
                        "Cannot delete a patient with existing appointments.\n"
                        "this patient is: %s" % rec.name
                    )
                )

    # def unlink(self):
    #     for rec in self:
    #         domain = [('patient_id', '=', rec.id)]
    #         appointments = self.env['hospital.appointment'].search(domain)
    #         if appointments:
    #             raise ValidationError(
    #                 _(
    #                     "Cannot delete a patient with existing
    # appointments.\n"
    #                     "this patient is: %s" % rec.name
    #                 )
    #             )
    #     return super().unlink()
