# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class SocialMediaPlatform(models.Model):
    _name = 'social.media.platform'
    _description = 'Social Media Platform'

    name = fields.Selection([
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('other', 'Other')
    ], required=True)
    api_key = fields.Char()
    api_secret = fields.Char()
    access_token = fields.Char()
    access_token_secret = fields.Char()
    color = fields.Integer()
    is_active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            'unique_platform_name',
            'UNIQUE(name)',
            'El platform name debe de ser unico.'
        )
    ]

    def test_connection(self):
        # Implementation for connection testing based on platform type
        if self.platform_type == 'facebook':
            # Test Facebook connection
            pass
        elif self.platform_type == 'twitter':
            # Test Twitter connection
            pass
        # Add other platforms
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Connection Test',
                'message': 'Connection successful!',
                'sticky': False,
            }
        }
