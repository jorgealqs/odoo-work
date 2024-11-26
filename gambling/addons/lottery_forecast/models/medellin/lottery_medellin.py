from odoo import models, fields, api
import logging
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
import pandas as pd
# import numpy as np

_logger = logging.getLogger(__name__)


class LotteryMedellin(models.Model):
    _name = 'lottery.medellin'
    _description = 'Lottery Medellin'
    _order = "draw_date desc"

    name = fields.Char(
        string='Lottery Draw',
        compute='_compute_name',
        store=True
    )
    number = fields.Char(string='Number', required=True)
    series = fields.Char(string='Series', required=True)
    number_sorteo = fields.Integer(string='Number sorteo', required=True)
    draw_date = fields.Date(string='Draw Date', required=True)

    @api.depends('number', 'series')
    def _compute_name(self):
        for record in self:
            record.name = f"{record.number} - Series {record.series}"

    _sql_constraints = [
        (
            'number_format',
            'CHECK (char_length(number) = 4)',
            'The lottery number must be 4 digits long.'
        ),
        (
            'series_format',
            'CHECK (char_length(series) = 3)',
            'The lottery series must be 3 digits long.'
        )
    ]

    def _get_request_params(self, data):
        """Retorna los parámetros necesarios para la petición HTTP."""
        return {
            'url': 'https://loteriademedellin.com.co/wp-admin/admin-ajax.php',
            'headers': {
                'Content-Type':
                'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest',
                'Origin': 'https://loteriademedellin.com.co',
                'Referer':
                'https://loteriademedellin.com.co/historico-de-resultados/',
                'User-Agent': 'Mozilla/5.0 (compatible; OdooBot/1.0)'
            },
            'payload': {
                'action': 'wp_get_results_lottery_template',
                'is_front': 'true',
                'lottery_id': '16',
                'draw_id': data.get("number_sorteo"),
                'post_type': 'results_template'
            }
        }

    def _make_request(self, url, headers, payload):
        """Realiza la petición HTTP y retorna los datos JSON."""
        try:
            response = requests.post(
                url,
                headers=headers,
                data=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            _logger.error(
                'Tiempo de espera agotado al conectar con el servidor de '
                'lotería'
            )
        except requests.exceptions.HTTPError as http_err:
            _logger.error(
                'Error HTTP al obtener datos de lotería: %s', http_err
            )
        except requests.exceptions.RequestException as err:
            _logger.error('Error al obtener datos de lotería: %s', err)
        except ValueError as err:
            _logger.error('Error al procesar la respuesta JSON: %s', err)
        return False

    def _parse_lottery_data(self, data):

        soup = BeautifulSoup(data.get("html_content"), 'html.parser')

        jackpot_container = soup.find('section', {'data-id': 'a4f229a'})
        if not jackpot_container:
            _logger.error('No se encontró el contenedor del premio mayor')
            return False

        elementor = jackpot_container.find(
            'div',
            {'class': 'elementor-lottery-jackpot-information'}
        )

        winners = elementor.find_all(
            'p',
            class_='elementor-lottery-jackpot-text'
        )

        number = winners[2].get_text().strip().replace('Número', '').strip()
        series = winners[3].get_text().strip().replace('Serie', '').strip()

        date_text = winners[1].get_text().strip()
        day, month, year = date_text.split('/')
        month_mapping = {
            'Enero': '01',
            'Febrero': '02',
            'Marzo': '03',
            'Abril': '04',
            'Mayo': '05',
            'Junio': '06',
            'Julio': '07',
            'Agosto': '08',
            'Septiembre': '09',
            'Octubre': '10',
            'Noviembre': '11',
            'Diciembre': '12'
        }
        month = month_mapping.get(month, '01')
        # Si no encuentra el mes, usa '01'
        formatted_date = f"{year}-{month}-{day.zfill(2)}"

        return {
            'number': number,
            'series': series,
            'number_sorteo': data.get('number_sorteo'),
            'draw_date': formatted_date
        }

    @api.model
    def fetch_lottery_data(self):
        for number_sorteo in range(4754, 4780):
            # Verificar si ya existe el número de sorteo
            existing_draw = self.search(
                [('number_sorteo', '=', number_sorteo)], limit=1)
            if existing_draw:
                _logger.info(
                    'El sorteo ya existe, continuando con el siguiente... '
                    f'{number_sorteo}'
                )
                continue

            data = {
                "number_sorteo": number_sorteo
            }
            params = self._get_request_params(data)
            result_data = self._make_request(
                params['url'],
                params['headers'],
                params['payload']
            )

            if not result_data:
                _logger.error('No se recibieron datos de la lotería')
                return False

            data["html_content"] = result_data['html']
            lottery_data = self._parse_lottery_data(data)
            if lottery_data:
                self.create(lottery_data)
                _logger.info('Datos de lotería procesados: %s', lottery_data)

    @api.model
    def pandasLotteryAnalysisMedellin(self, **kw):
        """
        Realiza análisis estadístico de los resultados de la lotería usando
        pandas.
        """
        _logger.info('\n\n __Pandas Lottery Analysis__ \n\n')

        # Obtener todos los registros de lotería
        lottery_records = self.search([])

        # Crear DataFrame con los números
        df = pd.DataFrame(
            [
                (rec.number) for rec in lottery_records
            ], columns=['number']
        )

        # Análisis de números de 4 cifras
        four_digit_freq = df['number'].value_counts()

        # Análisis de números de 3 cifras (últimos 3 dígitos)
        df['last_three'] = df['number'].str[-3:]
        three_digit_freq = df['last_three'].value_counts()

        results = {
            'four_digits': {
                'analysis': 'Top 10 números más frecuentes (4 cifras)',
                'data': four_digit_freq.to_dict()
            },
            'three_digits': {
                'analysis': 'Top 10 números más frecuentes (últimos 3 cifras)',
                'data': three_digit_freq.to_dict()
            }
        }

        _logger.info('Análisis de frecuencia completado: %s', results)
        return results
