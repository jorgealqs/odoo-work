import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class LotteryBalotoNumberFrequency(models.Model):
    _name = 'lottery.baloto.number.frequency'
    _description = 'Lottery Number Frequency Analysis 1-43 and 1-39'
    _order = "draw_date ASC, number ASC"

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

            for result in results:
                # Iterate over the 5 lottery numbers
                for n in [
                    result.number_1,
                    result.number_2,
                    result.number_3,
                    result.number_4,
                    result.number_5
                ]:
                    # Search if a record for this number, date, and type
                    # already exists
                    existing_frequency = self.env[
                        'lottery.baloto.number.frequency'
                    ].search([
                        ('number', '=', n),
                        ('draw_date', '=', result.draw_date),
                        ('lottery_type_id', '=', result.lottery_type_id.id)
                    ], limit=1)

                    if existing_frequency:
                        # Update existing record if found
                        existing_frequency.write({
                            'number': n,
                            'draw_date': result.draw_date,
                            'lottery_type_id': result.lottery_type_id.id
                        })
                    else:
                        # Create a new record if it doesn't exist
                        self.create({
                            'number': n,
                            'draw_date': result.draw_date,
                            'lottery_type_id': result.lottery_type_id.id
                        })

        _logger.info(
            "Number frequency by date calculated and stored successfully."
        )
