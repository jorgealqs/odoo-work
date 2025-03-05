# -*- coding: utf-8 -*-

from odoo import models, fields, tools
import logging

_logger = logging.getLogger(__name__)


class SocialMediaAnalytics(models.Model):
    _name = 'social.media.analytics'
    _description = 'Social Media Analytics'
    _auto = False

    date = fields.Date()
    platform_id = fields.Many2one('social.media.platform')
    post_count = fields.Integer()
    total_likes = fields.Integer()
    total_comments = fields.Integer()
    total_shares = fields.Integer()
    total_impressions = fields.Integer()
    total_clicks = fields.Integer()
    avg_engagement_rate = fields.Float()

    def init(self):
        # First check if the required tables exist to avoid errors during
        # installation
        self.env.cr.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name =
                'social_media_post_social_media_platform_rel'
            );
        """)
        table_exists = self.env.cr.fetchone()[0]

        if not table_exists:
            # If the table doesn't exist yet, create a simple view with no data
            tools.drop_view_if_exists(self.env.cr, self._table)
            self.env.cr.execute("""
                CREATE or REPLACE VIEW %s AS (
                    SELECT
                        0 as id,
                        CURRENT_DATE as date,
                        NULL as platform_id,
                        0 as post_count,
                        0 as total_likes,
                        0 as total_comments,
                        0 as total_shares,
                        0 as total_impressions,
                        0 as total_clicks,
                        0.0 as avg_engagement_rate
                    WHERE false
                )
            """ % (self._table,))
        else:
            # If the table exists, create the full analytics view
            tools.drop_view_if_exists(self.env.cr, self._table)
            self.env.cr.execute("""
                CREATE or REPLACE VIEW %s AS (
                    SELECT
                        ROW_NUMBER() OVER() as id,
                        DATE(p.post_date) as date,
                        rel.social_media_platform_id as platform_id,
                        COUNT(p.id) as post_count,
                        SUM(p.like_count) as total_likes,
                        SUM(p.comment_count) as total_comments,
                        SUM(p.share_count) as total_shares,
                        SUM(p.impression_count) as total_impressions,
                        SUM(p.click_count) as total_clicks,
                        AVG(p.engagement_rate) as avg_engagement_rate
                    FROM social_media_post p
                    JOIN social_media_post_social_media_platform_rel rel
                        ON p.id = rel.social_media_post_id
                    WHERE p.state = 'posted'
                    GROUP BY DATE(p.post_date), rel.social_media_platform_id
                )
            """ % (self._table,))
