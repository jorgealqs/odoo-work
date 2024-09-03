from odoo import models, fields


class FootballStats(models.Model):
    _name = 'football.stats'
    _description = 'Football General Stats'

    played = fields.Integer(string='Played')
    win = fields.Integer(string='Wins')
    draw = fields.Integer(string='Draws')
    lose = fields.Integer(string='Losses')
    scored = fields.Integer(string='Goals Scored')
    conceded = fields.Integer(string='Goals Conceded')
