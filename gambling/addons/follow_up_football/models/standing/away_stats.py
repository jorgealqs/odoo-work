from odoo import models, fields


class FootballAwayStats(models.Model):
    _name = 'football.away.stats'
    _description = 'Football Away Stats'

    played = fields.Integer(string='Played')
    win = fields.Integer(string='Wins')
    draw = fields.Integer(string='Draws')
    lose = fields.Integer(string='Losses')
    scored = fields.Integer(string='Goals Scored')
    conceded = fields.Integer(string='Goals Conceded')
