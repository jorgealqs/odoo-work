# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class SocialMediaComment(models.Model):
    _name = 'social.media.comment'
    _description = 'Social Media Comment'
    _order = 'create_date desc'

    external_post_id = fields.Many2one(
        'social.media.external.post',
        required=True
    )
    platform_id = fields.Many2one(
        related='external_post_id.platform_id',
        store=True
    )
    external_comment_id = fields.Char('External Comment ID', required=True)
    author_name = fields.Char('Author Name')
    author_id = fields.Many2one('res.partner', string='Author (if known)')
    content = fields.Text('Comment Content')
    create_date = fields.Datetime('Creation Date')
    like_count = fields.Integer('Likes', default=0)
    is_replied = fields.Boolean('Is Replied', default=False)
    sentiment = fields.Selection([
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative')
    ], string='Sentiment', default='neutral')

    def action_reply(self):
        return {
            'name': 'Reply to Comment',
            'type': 'ir.actions.act_window',
            'res_model': 'social.media.comment.reply.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_comment_id': self.id},
        }
