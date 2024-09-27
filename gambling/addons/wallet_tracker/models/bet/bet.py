from odoo import models, fields
from odoo.exceptions import ValidationError


class Betting(models.Model):
    _name = 'bet.tracker'
    _description = 'Bet Tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # Inherit to add tracking

    name = fields.Many2one(
        'bet.type',
        string='Bet Type',
        required=True,
        tracking=True
    )
    amount_invested = fields.Float(string='Amount Invested', required=True)
    state = fields.Selection([
        ('win', 'Win'),
        ('lose', 'Lose'),
        ('pending', 'Pending'),
    ], string='Result', default='pending', tracking=True)
    winnings = fields.Float(
        string='Winnings',
        default=0

    )
    date = fields.Date(string='Date', default=fields.Date.today)

    _sql_constraints = [
        (
            'check_amount_invested',
            'CHECK(amount_invested > 0)',
            'The Amount Invested must be greater than zero.'
        )
    ]

    def confirm_bet(self):
        for record in self:
            if record.winnings <= 0:
                raise ValidationError(
                    "You must input winnings greater than zero before "
                    "confirming the bet as 'win'."
                )
            record.state = 'win'

    def cancel_bet(self):
        for record in self:
            record.state = 'lose'
            record.winnings = 0

    def unlink(self):
        for record in self:
            if record.state != 'pending':
                raise ValidationError(
                    "You can only delete bets with a 'Pending' status."
                )
        return super(Betting, self).unlink()
