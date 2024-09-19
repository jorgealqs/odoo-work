import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class LotteryBalotoNumberFrequency116(models.Model):
    _name = 'lottery.baloto.number.frequency.1.16'
    _description = 'Lottery Number Frequency Analysis 1-16'
    _order = "draw_date ASC, number ASC"

    number = fields.Integer(string="Super Baloto Number", required=True)
    draw_date = fields.Date(string="Draw Date", required=True)
    lottery_type_id = fields.Many2one(
        'lottery.baloto.type',
        string="Lottery Type",
        required=True,
        ondelete='restrict'
    )

    def _calculate_number_frequency_1_16(self):
        """
        Calculate the frequency of the Super Baloto number (1-16) by date.
        """
        games = {
            'Baloto': range(1, 17),  # Numbers from 1 to 16 for Super Baloto
            'Revancha': range(1, 17)
        }

        for game_type, num_range in games.items():
            # Search historical results by lottery type
            results = self.env['lottery.baloto'].search(
                [('lottery_type_id.name', '=', game_type)]
            )

            for result in results:
                # Get the Super Baloto number
                super_baloto_number = result.super_baloto

                # Ensure the Super Baloto number is within the valid range
                if super_baloto_number in num_range:
                    # Search if a record for this Super Baloto number, date,
                    # and type already exists
                    existing_frequency = self.env[
                        'lottery.baloto.number.frequency.1.16'
                    ].search([
                        ('number', '=', super_baloto_number),
                        ('draw_date', '=', result.draw_date),
                        ('lottery_type_id', '=', result.lottery_type_id.id)
                    ], limit=1)

                    if existing_frequency:
                        # Update existing record if found
                        existing_frequency.write({
                            'number': super_baloto_number,
                            'draw_date': result.draw_date,
                            'lottery_type_id': result.lottery_type_id.id
                        })
                    else:
                        # Create a new record if it doesn't exist
                        self.create({
                            'number': super_baloto_number,
                            'draw_date': result.draw_date,
                            'lottery_type_id': result.lottery_type_id.id
                        })

        _logger.info(
            "Super Baloto number frequency by date calculated and stored "
            "successfully."
        )
