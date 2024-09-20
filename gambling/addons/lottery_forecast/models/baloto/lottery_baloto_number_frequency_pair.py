import logging
from itertools import combinations
from odoo import models, fields

_logger = logging.getLogger(__name__)


class LotteryBalotoNumberFrequencyPair(models.Model):
    _name = 'lottery.baloto.number.frequency.pair'
    _description = 'Frequency of Pairs of Numbers in Lottery Draws'
    _order = "frequency DESC, last_draw_date DESC"

    pair = fields.Char(string="Number Pair", required=True)
    number_1 = fields.Integer(string="Number 1", required=True)
    number_2 = fields.Integer(string="Number 2", required=True)
    frequency = fields.Integer(string="Frequency", required=True, default=0)
    lottery_type_id = fields.Many2one(
        'lottery.baloto.type',
        string="Lottery Type",
        required=True,
        ondelete='restrict'
    )
    last_draw_date = fields.Date(string="Last Draw Date")
    draw_dates = fields.Many2many(
        'lottery.baloto.draw',
        string="Draw Dates"
    )
    # Campo añadido
    create_date = fields.Date(
        string="Created On",
        default=fields.Date.today
    )
    update_date = fields.Datetime(
        string="Last Updated",
        readonly=True
    )
    # Campo añadido
    is_active = fields.Boolean(
        string="Is Active",
        default=True
    )

    def _analyze_pairs_frequency(self):
        """
        Analyze the frequency of pairs of numbers across lottery draws.
        """
        # Obtener todos los sorteos con el tipo de lotería "MiLoto"
        sorteos = self.env['lottery.baloto'].search([
            # ('lottery_type_id.name', '=', 'MiLoto')
        ])

        # Iterar sobre cada sorteo
        for sorteo in sorteos:
            # Extraer los 5 números del sorteo
            numeros = [
                sorteo.number_1,
                sorteo.number_2,
                sorteo.number_3,
                sorteo.number_4,
                sorteo.number_5
            ]

            # Generar las combinaciones de pares de los 5 números
            pares = list(combinations(numeros, 2))

            # Verificar cada par
            for par in pares:
                numero_1, numero_2 = par

                try:
                    # Verificar si la fecha del sorteo ya existe en el
                    # modelo `lottery.baloto.draw`
                    draw_date_record = self.env['lottery.baloto.draw'].search([
                        ('draw_date', '=', sorteo.draw_date)
                    ], limit=1)

                    if not draw_date_record:
                        # Si no existe, crear la fecha del sorteo
                        draw_date_record = self.env[
                            'lottery.baloto.draw'
                        ].create({
                            'draw_date': sorteo.draw_date
                        })

                    # Verificar si ya existe este par con la misma lotería y
                    # la misma fecha de sorteo
                    existing_pair = self.env[
                        'lottery.baloto.number.frequency.pair'
                    ].search([
                        ('number_1', '=', numero_1),
                        ('number_2', '=', numero_2),
                        ('lottery_type_id', '=', sorteo.lottery_type_id.id),
                        ('draw_dates', 'in', draw_date_record.id)
                    ], limit=1)

                    if existing_pair:
                        # Si el par ya existe y está registrado para la misma
                        # fecha, no incrementamos la frecuencia
                        _logger.info(
                            f"Pair {numero_1} - {numero_2} already exists for "
                            f"draw date {sorteo.draw_date}. Frequency not "
                            f"incremented."
                        )
                        continue
                    else:
                        # Verificar si el par existe pero no para la misma
                        # fecha
                        existing_pair = self.env[
                            'lottery.baloto.number.frequency.pair'
                        ].search([
                            ('number_1', '=', numero_1),
                            ('number_2', '=', numero_2),
                            ('lottery_type_id', '=', sorteo.lottery_type_id.id)
                        ], limit=1)

                        if existing_pair:
                            # Si el par ya existe pero para una fecha
                            # diferente, incrementamos la frecuencia y
                            # actualizamos las fechas
                            values = {
                                'frequency': existing_pair.frequency + 1,
                                'last_draw_date': max(
                                    existing_pair.last_draw_date,
                                    sorteo.draw_date
                                ),
                                'update_date': fields.Datetime.now(),
                            }
                            # Si el sorteo actual no está en las fechas del
                            # par, lo añadimos
                            values['draw_dates'] = [(4, draw_date_record.id)]
                            existing_pair.write(values)
                        else:
                            # Si no existe, creamos un nuevo registro
                            self.create({
                                'number_1': numero_1,
                                'number_2': numero_2,
                                'pair': f"{numero_1} - {numero_2}",
                                'frequency': 1,
                                'last_draw_date': sorteo.draw_date,
                                'draw_dates': [(4, draw_date_record.id)],
                                'lottery_type_id': sorteo.lottery_type_id.id,
                                'update_date': fields.Datetime.now()
                            })
                except Exception as e:
                    _logger.error(
                        f"Error processing pair {numero_1} - {numero_2}: {e}"
                    )
                    continue

        _logger.info("Analysis of number pairs completed successfully.")
