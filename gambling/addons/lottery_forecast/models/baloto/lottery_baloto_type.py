from odoo import models, fields


class LotteryBalotoType(models.Model):
    _name = 'lottery.baloto.type'
    _description = 'Lottery Baloto Type'
    _order = "name ASC"

    name = fields.Char(
        string="Name",
        required=True
    )
    sequence = fields.Integer(string="Sequence", default=1)

    _sql_constraints = [
        (
            'name_unique',
            'unique(name)',
            'The name of the lottery type must be unique.'
        )
    ]
