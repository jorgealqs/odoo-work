# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class SocialMediaExternalPost(models.Model):
    _name = 'social.media.external.post'
    _description = 'External Social Media Post Reference'

    post_id = fields.Many2one(
        'social.media.post',
        required=True,
        ondelete='cascade'
    )
    platform_id = fields.Many2one(
        'social.media.platform',
        required=True
    )
    external_id = fields.Char(required=True)
    post_url = fields.Char()
    post_date = fields.Datetime()
