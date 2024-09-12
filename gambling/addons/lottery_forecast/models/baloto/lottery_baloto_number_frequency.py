import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class LotteryBalotoNumberFrequency(models.Model):
    _name = 'lottery.baloto.number.frequency'
    _description = 'Lottery Number Frequency Analysis'
    _order = "number ASC, draw_date DESC"

    number = fields.Integer(string="Lottery Number", required=True)
    draw_date = fields.Date(string="Draw Date", required=True)
    lottery_type_id = fields.Many2one(
        'lottery.baloto.type',
        string="Lottery Type",
        required=True,
        ondelete='restrict'
    )

    def _calculate_number_frequency(self):
        """
        Calculate the frequency of each lottery number by date.
        """

        # Clear previous frequency records
        self.env['lottery.baloto.number.frequency'].unlink()

        games = {
            'Baloto': range(1, 44),  # Numbers from 1 to 43
            'Revancha': range(1, 44),
            'MiLoto': range(1, 40)  # Numbers from 1 to 39 for MiLoto
        }

        for game_type, num_range in games.items():
            # Search historical results by lottery type
            results = self.env['lottery.baloto'].search(
                [('lottery_type_id.name', '=', game_type)]
            )

            # Calculate frequency of each number by date
            for result in results:
                for n in [
                    result.number_1,
                    result.number_2,
                    result.number_3,
                    result.number_4,
                    result.number_5
                ]:
                    self.create({
                        'number': n,
                        'draw_date': result.draw_date,
                        'lottery_type_id': result.lottery_type_id.id
                    })

        _logger.info(
            "Number frequency by date calculated and stored successfully."
        )
