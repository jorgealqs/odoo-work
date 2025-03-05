# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
from odoo.exceptions import ValidationError  # type: ignore

_logger = logging.getLogger(__name__)


class SocialMediaPost(models.Model):
    _name = 'social.media.post'
    _description = 'Social Media Post'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'post_date desc'

    name = fields.Char(required=True)
    content = fields.Html(required=True)
    video_url = fields.Char()
    post_date = fields.Datetime(default=fields.Datetime.now)
    scheduled_date = fields.Datetime()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('posted', 'Posted'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)
    tag_ids = fields.Many2many("social.media.tag")
    color = fields.Integer(compute="_compute_color", store=True)

    # Relations with other Odoo models
    image_ids = fields.One2many(
        'ir.attachment',
        'res_id',
        domain=[('res_model', '=', 'social.media.post')],
        string="Imágenes"
    )
    platform_ids = fields.Many2many('social.media.platform')

    # Post metrics
    like_count = fields.Integer('Likes', default=0)
    comment_count = fields.Integer('Comments', default=0)
    share_count = fields.Integer('Shares', default=0)
    click_count = fields.Integer('Clicks', default=0)
    impression_count = fields.Integer('Impressions', default=0)
    engagement_rate = fields.Float(compute='_compute_engagement_rate')

    external_post_ids = fields.One2many(
        'social.media.external.post',
        'post_id'
    )

    @api.depends('state')
    def _compute_color(self):
        color_mapping = {
            'draft': 8,
            'scheduled': 7,
            'posted': 10,
            'failed': 1,
            'cancelled': 1
        }
        for record in self:
            record.color = color_mapping.get(record.state, 0)

    @api.depends(
        'like_count', 'comment_count', 'share_count', 'impression_count'
    )
    def _compute_engagement_rate(self):
        for post in self:
            if post.impression_count:
                post.engagement_rate = (
                    (
                        post.like_count + post.comment_count + post.share_count
                    ) / post.impression_count
                ) * 100
            else:
                post.engagement_rate = 0.0

    def action_schedule(self):
        self.write({'state': 'scheduled'})

    def action_post(self):
        # Implementation for posting to social media platforms
        success = True
        for platform in self.platform_ids:
            try:
                # Create external post reference
                # external_id = self._post_to_platform(platform)
                # if external_id:
                #     self.env['social.media.external.post'].create({
                #         'post_id': self.id,
                #         'platform_id': platform.id,
                #         'external_id': external_id,
                #         'post_url':
                # self._get_post_url(platform, external_id),
                #     })
                success = True
                # else:
                #     success = False
            except Exception as e:
                _logger.error("Failed to post %s: %s", platform.name, str(e))
                success = False

        self.write({'state': 'posted' if success else 'failed'})

    def _post_to_platform(self, platform):
        # Implementation for specific platform posting
        # Returns external post ID if successful, False otherwise
        if platform.platform_type == 'facebook':
            # Post to Facebook
            pass
        elif platform.platform_type == 'twitter':
            # Post to Twitter
            pass
        # Add more platforms as needed
        return False

    def _get_post_url(self, platform, external_id):
        # Generate public URL for the post based on platform and external ID
        if platform.platform_type == 'facebook':
            return f'https://facebook.com/{external_id}'
        elif platform.platform_type == 'twitter':
            return f'https://twitter.com/status/{external_id}'
        # Add more platforms
        return '#'

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_refresh_metrics(self):
        # Implementation to fetch updated metrics from platforms
        for record in self:
            for ext_post in record.external_post_ids:
                platform = ext_post.platform_id
                metrics = (
                    self._get_post_metrics(platform, ext_post.external_id)
                )
                if metrics:
                    record.write({
                        'like_count': metrics.get('likes', 0),
                        'comment_count': metrics.get('comments', 0),
                        'share_count': metrics.get('shares', 0),
                        'impression_count': metrics.get('impressions', 0),
                        'click_count': metrics.get('clicks', 0),
                    })

    def _get_post_metrics(self, platform, external_id):
        # Implementation to fetch metrics for a specific post
        return False

    def unlink(self):
        for record in self:
            if record.state in ['posted', 'scheduled']:
                raise ValidationError(
                    "You cannot delete a property that is in"
                    "'Posted' or 'Scheduled' state."
                )
        return super().unlink()
