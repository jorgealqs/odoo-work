import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQGoals(models.Model):
    _name = 'sport.metrics.jq.goals'
    _description = 'SportMetricsJQ Goals'

    played = fields.Integer(string='Played')
    win = fields.Integer(string='Wins')
    draw = fields.Integer(string='Draws')
    lose = fields.Integer(string='Losses')
    goals_for = fields.Integer(string='Goals For')
    goals_against = fields.Integer(string='Goals Against')
