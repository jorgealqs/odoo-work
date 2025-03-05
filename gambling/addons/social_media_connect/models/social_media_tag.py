# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class SocialMediaTag(models.Model):
    _name = "social.media.tag"
    _description = "Etiqueta de Redes Sociales"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        (
            'unique_tag_name',
            'UNIQUE(name)',
            'El tag debe de ser unico.'
        )
    ]
