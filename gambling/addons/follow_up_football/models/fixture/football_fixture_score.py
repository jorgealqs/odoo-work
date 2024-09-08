import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class FootballScore(models.Model):
    _name = 'football.fixture.score'
    _description = 'Football Fixture Score'

    halftime_home = fields.Integer(string='Halftime Home Goals')
    halftime_away = fields.Integer(string='Halftime Away Goals')
    fulltime_home = fields.Integer(string='Fulltime Home Goals')
    fulltime_away = fields.Integer(string='Fulltime Away Goals')
    extratime_home = fields.Integer(
        string='Extratime Home Goals',
        default=None
    )
    extratime_away = fields.Integer(
        string='Extratime Away Goals',
        default=None
    )
    penalty_home = fields.Integer(
        string='Penalty Home Goals',
        default=None
    )
    penalty_away = fields.Integer(
        string='Penalty Away Goals',
        default=None
    )