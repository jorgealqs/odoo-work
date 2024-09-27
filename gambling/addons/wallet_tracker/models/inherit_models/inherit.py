import logging
from odoo import models

_logger = logging.getLogger(__name__)


class InheritedBetTracker(models.Model):
    _inherit = "bet.tracker"

    def confirm_bet(self):
        for record in self:
            if record.winnings > 0:
                if record.winnings < record.amount_invested:
                    self.create_invoice(record, "loss")
                else:
                    self.create_invoice(record, "profit")
        return super(InheritedBetTracker, self).confirm_bet()

    def cancel_bet(self):
        """
        Marks the bet as lost and creates an invoice reflecting the loss.
        """
        for record in self:
            # Create an invoice reflecting the loss
            self.create_invoice(record, "loss")

        # Call the parent method to mark the bet as lost
        return super(InheritedBetTracker, self).cancel_bet()

    def create_invoice(self, record, bet_result):
        """
        Helper method to create a detailed invoice for the bet.
        :param record: The bet record
        :param amount: The amount to invoice (profit or loss)
        :param bet_result: "profit" or "loss"
        """
        invoice_line_vals = [
            # First line: Amount invested
            (0, 0, {
                'name': f'Lottery: {record.name.name}',
                'quantity': 1,
                'price_unit': record.amount_invested,
            }),
        ]

        # Total variable to keep track of the total amount in the invoice
        total_amount = 0

        if record.state == 'win':
            # Second line: Bet result based on winnings
            if record.winnings >= record.amount_invested:
                # Full win: Show the profit amount minus the amount invested
                profit = record.winnings - record.amount_invested
                invoice_line_vals.append((0, 0, {
                    'name': 'Resultado: Ganó',
                    'quantity': 1,
                    'price_unit': profit,  # Show the profit in positive
                }))
                total_amount += profit
            elif (
                record.winnings > 0
                and record.winnings < record.amount_invested
            ):
                # Partial win: Show winnings and set total to zero
                partial_win = record.winnings
                invoice_line_vals.append((0, 0, {
                    'name': 'Resultado: Ganó parcialmente',
                    'quantity': 1,
                    'price_unit': partial_win,
                }))
                # Set total to zero, since it is a partial win
                total_amount += 0  # Total is zero
        else:
            # Total loss: reflect the entire investment as loss
            invoice_line_vals.append((0, 0, {
                'name': 'Resultado: Perdió todo',
                'quantity': 1,
                'price_unit': -record.amount_invested,  # Total loss
            }))
            total_amount += 0  # Total is zero in the case of total loss

        # Create the invoice line for the total amount, which will always
        # be zero
        invoice_line_vals.append((0, 0, {
            'name': 'Total',
            'quantity': 1,
            'price_unit': total_amount,  # Show total as zero
        }))

        invoice_vals = {
            'partner_id': self.env.user.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_line_vals,
        }

        _logger.info(invoice_vals)

        # Create the invoice
        invoice = self.env['account.move'].create(invoice_vals)
        _logger.info(
            f'Invoice {invoice.id} created for bet {record.name} with result: '
            f'{bet_result}'
        )
