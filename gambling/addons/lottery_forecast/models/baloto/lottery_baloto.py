import logging
import itertools
import pandas as pd
from datetime import datetime, timedelta
import random
import requests
import time
import os
from bs4 import BeautifulSoup
from odoo import models, fields, api
# from odoo import models, fields, tools
from requests.exceptions import RequestException

_logger = logging.getLogger(__name__)


class LotteryBaloto(models.Model):
    _name = 'lottery.baloto'
    _description = 'Lottery Baloto'
    _order = "draw_date DESC"

    number_1 = fields.Integer(string="Number 1", required=True)
    number_2 = fields.Integer(string="Number 2", required=True)
    number_3 = fields.Integer(string="Number 3", required=True)
    number_4 = fields.Integer(string="Number 4", required=True)
    number_5 = fields.Integer(string="Number 5", required=True)
    super_baloto = fields.Integer(string="Super Baloto", help="Super Baloto")
    draw_date = fields.Date(string="Draw Date", required=True)
    is_winner = fields.Boolean(string="Is Winner", default=False)
    # Relación con el tipo de lotería
    lottery_type_id = fields.Many2one(
        'lottery.baloto.type',
        string="Lottery Type",
        required=True,
        ondelete='restrict'
    )
    lottery_type_name = fields.Char(
        compute='_compute_lottery_type_name',
        store=True
    )

    @api.model
    def test(self):
        model_wizard = self.env['lottery.baloto.wizard']
        model_wizard.action_calculate_number_frequency()
        model_wizard.action_calculate_number_frequency_1_16()
        model_wizard.action_analyze_pairs_frequency()

    @api.depends('lottery_type_id.name')
    def _compute_lottery_type_name(self):
        for record in self:
            record.lottery_type_name = (
                record.lottery_type_id.name if record.lottery_type_id else ''
            )

    def _get_wednesday_and_saturday(self):
        """
        Calculate the upcoming Wednesday and Saturday based on the current
        date. Returns two dates: the next Wednesday and Saturday.
        """
        today = datetime.today()

        # Calculate Wednesday (2 = Wednesday)
        wednesday = today + timedelta(
            days=(
                2 - today.weekday()
            ) if today.weekday() <= 2 else -(today.weekday() - 2)
        )

        # Calculate Saturday (5 = Saturday)
        saturday = today + timedelta(
            days=(
                5 - today.weekday()
            ) if today.weekday() <= 5 else -(today.weekday() - 5)
        )

        return wednesday.date(), saturday.date()

    def _sync_results(self):
        try:
            next_wednesday, next_saturday = self._get_wednesday_and_saturday()
            dates_to_fetch = [next_wednesday, next_saturday]
            for date in dates_to_fetch:
                formatted_date = date.strftime('%Y-%m-%d')
                if not self.search(
                    [
                        ('draw_date', '=', formatted_date)
                    ], limit=1
                ):
                    self._fetch_and_log_results(formatted_date)
        except Exception as e:
            _logger.error(f"Error syncing results: {str(e)}")

    def _generate_dates(self, start_date, end_date):
        dates = []
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() in [2, 5]:  # Miércoles y sábado
                dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        return dates

    def _fetch_and_log_results(self, date):
        url = f'https://baloto.com/resultados?date={date}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            table = soup.find('table', id='results-table')

            if not table:
                _logger.warning(f"No 'results-table' found for date: {date}")
                return

            headers, rows = self._parse_table(table)
            _logger.info(f"Table headers: {headers}")

            tipos = ['Baloto', 'Revancha']

            for idx, row in enumerate(rows):
                numeros = row[2].split(" - ")
                if len(numeros) != 6:
                    _logger.warning(
                        f"Unexpected number format for date: {date}"
                    )
                    continue

                lottery_type = self.env[
                    'lottery.baloto.type'
                ].search([('name', '=', tipos[idx])], limit=1)
                if not lottery_type:
                    _logger.warning(
                        f"Lottery type '{tipos[idx]}' not found."
                    )
                    continue

                self.create({
                    'number_1': int(numeros[0]),
                    'number_2': int(numeros[1]),
                    'number_3': int(numeros[2]),
                    'number_4': int(numeros[3]),
                    'number_5': int(numeros[4]),
                    'super_baloto': int(numeros[5]),
                    'draw_date': date,
                    'lottery_type_id': lottery_type.id,
                })

        except requests.RequestException as e:
            _logger.error(f"Request error for date {date}: {e}")
        except Exception as e:
            _logger.error(f"Unexpected error for date {date}: {e}")

    def _parse_table(self, table):
        headers = [header.text for header in table.find_all('th')]
        rows = [
            [col.text.strip() for col in row.find_all('td')]
            for row in table.find_all('tr')[1:]
        ]
        return headers, rows

    def _sync_results_miloto(self):
        """Sincroniza los resultados de MiLoto desde la web de Baloto."""
        base_url = os.getenv('MILOTO_URL', '')
        month_replacements = {
            'Enero': 'January',
            'Febrero': 'February',
            'Marzo': 'March',
            'Abril': 'April',
            'Mayo': 'May',
            'Junio': 'June',
            'Julio': 'July',
            'Agosto': 'August',
            'Septiembre': 'September',
            'Octubre': 'October',
            'Noviembre': 'November',
            'Diciembre': 'December'
        }

        lottery_type = self.env[
            'lottery.baloto.type'
        ].search([('name', '=', 'MiLoto')], limit=1)
        if not lottery_type:
            return
        # Count the number of existing 'MiLoto' records
        total_records = self.search_count(
            [('lottery_type_id.name', '=', 'MiLoto')]
        )

        # Start the loop from the next sorteo number
        start_sorteo = total_records + 1
        # Iterar sobre el rango de sorteos para obtener los resultados
        for sorteo in range(start_sorteo, start_sorteo + 2):
            wait_time = random.uniform(10, 15)
            url = f"{base_url}{sorteo}"
            try:
                # Verificar si ya existe un registro con el mismo super_baloto
                existing_record = self.search([
                    ('super_baloto', '=', sorteo),
                    ('lottery_type_id', '=', lottery_type.id)
                ], limit=1)

                if existing_record:
                    continue

                # Realizar la petición HTTP a la página
                response = requests.get(url)
                response.raise_for_status()
                # Verificar que la petición fue exitosa

                soup = BeautifulSoup(response.content, 'html.parser')

                # Capturar la fecha del sorteo
                formatted_date = self._extract_date(soup, month_replacements)
                if not formatted_date:
                    continue

                # Capturar los números de las bolas
                numbers = self._extract_numbers(soup)
                winner = self._check_if_winner(soup)
                if numbers:
                    self.create({
                        'number_1': numbers[0],
                        'number_2': numbers[1],
                        'number_3': numbers[2],
                        'number_4': numbers[3],
                        'number_5': numbers[4],
                        'super_baloto': sorteo,
                        'is_winner': winner,
                        'draw_date': formatted_date,
                        'lottery_type_id': lottery_type.id,
                    })

                # Pausa aleatoria para evitar ser bloqueado por el servidor
                time.sleep(wait_time)

            except RequestException as e:
                _logger.error(
                    f"Error al obtener los datos del sorteo {sorteo} "
                    f"desde {url}: {e}"
                )
            except Exception as e:
                _logger.error(
                    f"Error inesperado al procesar el sorteo {sorteo}: {e}"
                )

    def _extract_date(self, soup, month_replacements):
        """Extrae y formatea la fecha del sorteo desde el HTML."""
        try:
            div_date = soup.find(
                'div',
                class_=(
                    'col-md-7 white-color text-center'
                    ' text-md-start text-lg-start'
                )
            )
            if div_date:
                date_text = div_date.find(
                    'div',
                    class_='fs-5'
                ).get_text(strip=True)

                # Reemplazar meses en español por su equivalente en inglés
                for es_month, en_month in month_replacements.items():
                    date_text = date_text.replace(es_month, en_month)

                # Convertir la fecha en un objeto datetime
                return datetime.strptime(date_text, '%d de %B de %Y')

        except Exception as e:
            _logger.error(f"Error al extraer o formatear la fecha: {e}")
        return None

    def _extract_numbers(self, soup):
        """Extrae los números de las bolas amarillas desde el HTML."""
        try:
            div = soup.find('div', class_='row d-flex justify-content-center')
            if div:
                yellow_balls = div.find_all('div', class_='yellow-ball')

                # Extraer los números de las bolas amarillas
                return [ball.get_text(strip=True) for ball in yellow_balls]
        except Exception as e:
            _logger.error(f"Error al extraer los números de las bolas: {e}")
        return None

    def _check_if_winner(self, soup):
        try:
            # Encontrar el primer bloque con la clase específica
            first_result = (
                soup.find_all('div', class_='mt-4 bg-white rounded')[0]
            )

            # Extraer el monto del premio total
            prize_total = first_result.find('strong', class_='fs-1 pink-light')

            if prize_total:
                prize_amount = (
                    prize_total.text.strip().replace('$', '').replace('.', '')
                )

                # Convertir a número y verificar si es mayor a 0
                return int(prize_amount) > 0

            return False

        except Exception as e:
            print(f"Error al obtener los datos: {e}")
            return False

    @api.model
    def _create_dataframe(self, records, columns):
        data = [{
            'number': record[col],
            'draw_date': record['draw_date'],
            'super_baloto': record['super_baloto']
        } for record in records for col in columns]

        df = pd.DataFrame(data)
        df['draw_date'] = pd.to_datetime(df['draw_date'])
        df['day_of_week'] = df['draw_date'].dt.day_name()
        return df

    @api.model
    def _process_frequency_analysis(self, df):
        df['date_day_super'] = (
            df['draw_date'].dt.strftime('%Y-%m-%d') + ':' +
            df['day_of_week'] + ':' +
            df['super_baloto'].fillna('N/A').astype(str)
        )

        frequency_df = df[
            'number'
        ].value_counts().reset_index(name='frequency')
        dates_sorteos_df = df.groupby('number').agg({
            'date_day_super': list,
            'draw_date': 'max'
        }).reset_index()

        result_df = pd.merge(frequency_df, dates_sorteos_df, on='number')
        return result_df.sort_values(
            by='frequency', ascending=False
        ).to_dict(orient='records')

    @api.model
    def analyze_frequencies_pandas(self, option=None):
        _logger.info("Analyzing frequencies using pandas...")

        try:
            # Obtener los registros filtrados
            records = self.search_read(
                [
                    ("lottery_type_id.name", "=", option)
                ],
                []
            )

            if not records:
                _logger.warning("No records found for analysis.")
                return []

            # Crear el DataFrame para number_1 a number_5
            df = self._create_dataframe(
                records, [f'number_{i}' for i in range(1, 6)]
            )

            # Procesar el análisis de frecuencia
            result = self._process_frequency_analysis(df)

            _logger.info("Frequencies analysis completed using pandas.")
            return result

        except Exception as e:
            _logger.error(f"Error during frequency analysis: {e}")
            return []

    @api.model
    def frequency_1_16_pandas(self, option=None):
        _logger.info("Analyzing super_baloto frequencies...")

        try:
            # Obtener los registros filtrados por tipo de lotería
            records = self.search_read(
                [
                    ("lottery_type_id.name", "=", option)
                ],
                ['super_baloto', 'draw_date'])

            if not records:
                _logger.warning("No records found for analysis.")
                return []

            # Crear el DataFrame para 'super_baloto'
            df = self._create_dataframe(records, ['super_baloto'])

            # Procesar el análisis de frecuencia
            result = self._process_frequency_analysis(df)

            _logger.info(
                "Super_baloto frequencies analysis completed using pandas."
            )
            return result

        except Exception as e:
            _logger.error(f"Error during super_baloto frequency analysis: {e}")
            return []

    @api.model
    def analyze_frequency_numbers_pandas(self, option=None, default_number=2):
        _logger.info(
            f"Analyzing number combinations of {default_number} using pandas."
        )

        try:
            # Fetch the records
            records = self.search_read(
                [("lottery_type_id.name", "=", option)],
                []
            )

            if not records:
                _logger.warning("No records found for analysis.")
                return []

            # Initialize a list to store the combination information
            combinations_data = []

            # Loop through each record to collect number combinations
            for record in records:
                numbers = [record.get(f'number_{i}') for i in range(1, 6)]

                # Create all possible combinations of 'default_number' numbers
                for combination in itertools.combinations(sorted(
                    numbers
                ), default_number):
                    combinations_data.append({
                        'number': "-".join(map(str, combination)),
                        'draw_date': record.get('draw_date')
                    })

            # Create a DataFrame from the collected combinations data
            df = pd.DataFrame(combinations_data)

            # Convert the 'draw_date' column to datetime to extract the day
            # of the week
            df['draw_date'] = pd.to_datetime(df['draw_date'])
            df['day_of_week'] = df['draw_date'].dt.day_name()

            # Concatenate date, day of the week
            df['date_day_super'] = (
                df['draw_date'].dt.strftime('%Y-%m-%d') + ':' +
                df['day_of_week'].astype(str)
            )

            # Get the frequency of each combination
            frequency_df = df.groupby(
                'number'
            ).size().reset_index(name='frequency')

            # Group the draw dates by combination
            dates_sorteos_df = df.groupby('number').agg({
                'date_day_super': lambda x: list(x),
            }).reset_index()

            # Merge the frequency and draw date details
            result_df = pd.merge(frequency_df, dates_sorteos_df, on='number')

            # Sort by 'frequency' in descending order
            result_df = result_df.sort_values(by='frequency', ascending=False)

            # Convert the result to a list of dictionaries
            result = result_df.to_dict(orient='records')

            _logger.info(
                f"Number combination analysis of {default_number} completed."
            )
            return result

        except Exception as e:
            _logger.error(f"Error during number combination analysis: {e}")
            return []
