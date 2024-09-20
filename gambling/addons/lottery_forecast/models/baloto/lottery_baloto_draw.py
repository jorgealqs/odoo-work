import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class LotteryBalotoDraw(models.Model):
    _name = 'lottery.baloto.draw'
    _description = 'Lottery Draw Dates'
    _order = "draw_date DESC"

    draw_date = fields.Date(string="Draw Date", required=True)
