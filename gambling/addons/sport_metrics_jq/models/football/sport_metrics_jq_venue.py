import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQTeamVenue(models.Model):
    _name = 'sport.metrics.jq.team.venue'
    _description = 'SportMetricsJQ Venue'
    _order = "name ASC"

    id_venue = fields.Integer(string='Venue ID')
    name = fields.Char(string='Name')
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    capacity = fields.Integer(string='Capacity')
    surface = fields.Char(string='Surface')
    image = fields.Char(string='Image URL')
