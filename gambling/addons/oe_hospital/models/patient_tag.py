# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class HospitalPatientTag(models.Model):
    _name = 'hospital.patient.tag'
    _description = 'Hospital Patient Tag'
    _order = 'sequence,id'

    name = fields.Char(
        string='Name', required=True
    )
    color = fields.Integer(string='Color Index')
    sequence = fields.Integer(string='Sequence', default=10)
