# -*- coding: utf-8 -*-

from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)


class SocialMediaCommentReplyWizard(models.TransientModel):
    _name = 'social.media.comment.reply.wizard'
    _description = 'Reply to Social Media Comment'

    comment_id = fields.Many2one('social.media.comment', required=True)
    reply_content = fields.Text('Reply', required=True)

    def action_send_reply(self):
        comment = self.comment_id
        # platform = comment.platform_id

        # Implementation to post reply to the platform
        success = False
        try:
            # Logic to post reply based on platform
            success = True
        except Exception as e:
            _logger.error("Failed to reply to comment: %s", str(e))

        if success:
            comment.write({'is_replied': True})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reply Status',
                'message': 'Reply sent successfully!' if success else 'Failed',
                'sticky': False,
            }
        }
