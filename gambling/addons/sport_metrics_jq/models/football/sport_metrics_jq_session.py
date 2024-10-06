import logging
from odoo import models, fields

# Configuring the logger to record relevant information in Odoo logs
_logger = logging.getLogger(__name__)


class SportMetricsJQSession(models.Model):
    _name = 'sport.metrics.jq.session'
    _description = 'SportMetricsJQ Season'
    _order = "year desc"
    _rec_name = 'year'

    # Model fields
    year = fields.Char(string='Year', required=True)
