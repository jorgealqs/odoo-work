from odoo import models, fields


class BetType(models.Model):
    _name = 'bet.type'
    _description = 'Bet Type'

    name = fields.Char(string='Type Name', required=True)
