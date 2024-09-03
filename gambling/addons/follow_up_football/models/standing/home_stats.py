from odoo import models, fields


class FootballHomeStats(models.Model):
    _name = 'football.home.stats'
    _description = 'Football Home Stats'

    played = fields.Integer(string='Played')
    win = fields.Integer(string='Wins')
    draw = fields.Integer(string='Draws')
    lose = fields.Integer(string='Losses')
    scored = fields.Integer(string='Goals Scored')
    conceded = fields.Integer(string='Goals Conceded')
