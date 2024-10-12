import logging
# import os
import pandas as pd
from datetime import datetime, timedelta
import random
import requests
import time
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
        """
        Synchronizes Baloto lottery results from an Excel file and, if
        necessary, from a web scraping API. It only syncs results for the next
        Wednesday and Saturday of the week.

        The process includes:
        1. Reading an XLSX file using pandas, where the Baloto lottery results
        are extracted.
        2. Checking if the lottery type already exists in the system. If it
        doesn't exist, the creation is skipped.
        3. Checking if a record with the same date already exists. If the
        record already exists, creation is skipped.
        4. If the record does not exist, a new one is created with the data
        read from the file.
        5. Then, it fetches results for the upcoming Wednesday and Saturday,
        if they don't already exist, via a web scraping API.
        """

        # Get the file path within the module
        # module_path = tools.config['addons_path'].split(',')[0]
        # file_path = os.path.join(
        #     module_path,
        #     'lottery_forecast',
        #     'data_baloto',
        #     'baloto_results.xlsx'
        # )

        try:
            # Read the XLSX file using pandas
            # df = pd.read_excel(file_path)

            # for _, row in df.iterrows():
            #     lottery_type_name = row['Type']
            #     numbers = [row[f'# {i}'] for i in range(1, 6)]
            #     super_baloto = row['Super Baloto']
            #     draw_date = row['Fecha de Creación']

            #     # Get the ID of the lottery type based on the name
            #     lottery_type = self.env['lottery.baloto.type'].search(
            #         [('name', '=', lottery_type_name)], limit=1
            #     )
            #     if not lottery_type:
            #         continue

            #     # Check if a record with the same date already exists
            #     existing_record = self.search([
            #         ('draw_date', '=', draw_date),
            #         ('lottery_type_id', '=', lottery_type.id)
            #     ], limit=1)
            #     if existing_record:
            #         continue

            #     # Create new record
            #     self.create({
            #         'number_1': numbers[0],
            #         'number_2': numbers[1],
            #         'number_3': numbers[2],
            #         'number_4': numbers[3],
            #         'number_5': numbers[4],
            #         'super_baloto': super_baloto,
            #         'draw_date': draw_date,
            #         'lottery_type_id': lottery_type.id,
            #     })

            # Calculate upcoming Wednesday and Saturday
            next_wednesday, next_saturday = self._get_wednesday_and_saturday()
            dates_to_fetch = [next_wednesday, next_saturday]

            # wait_time = random.uniform(8, 12)
            for date in dates_to_fetch:
                # Format the date to YYYY-MM-DD
                formatted_date = date.strftime('%Y-%m-%d')

                existing_record = self.search(
                    [
                        ('draw_date', '=', formatted_date)
                    ], limit=1
                )
                if not existing_record:
                    # Only make the request if no record exists
                    self._fetch_and_log_results(formatted_date)
                    # time.sleep(wait_time)

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

            if table:
                headers, rows = self._parse_table(table)
                _logger.info(f"Encabezados de la tabla: {headers}")

                tipos = ['Baloto', 'Revancha']

                for idx, row in enumerate(rows):
                    numeros = row[2].split(" - ")
                    if len(numeros) == 6:
                        numeros = [int(n) for n in numeros]
                        lottery_type = self.env[
                            'lottery.baloto.type'
                        ].search([('name', '=', tipos[idx])], limit=1)
                        if not lottery_type:
                            _logger.warning(
                                f"Tipo de lotería '{tipos[idx]}' no "
                                "encontrado. Omite el registro."
                            )
                            continue

                        # Guardar los resultados en el modelo lottery.baloto
                        self.create({
                            'number_1': numeros[0],
                            'number_2': numeros[1],
                            'number_3': numeros[2],
                            'number_4': numeros[3],
                            'number_5': numeros[4],
                            'super_baloto': numeros[5],
                            'draw_date': date,
                            'lottery_type_id': lottery_type.id,
                        })
            else:
                _logger.warning(
                    "No se encontró la tabla con el ID 'results-table'."
                )

        except requests.RequestException as e:
            _logger.error(f"Error en la solicitud: {e}")
        except Exception as e:
            _logger.error(f"Error inesperado: {e}")

    def _parse_table(self, table):
        headers = [header.text for header in table.find_all('th')]
        rows = [
            [col.text.strip() for col in row.find_all('td')]
            for row in table.find_all('tr')[1:]
        ]
        return headers, rows

    def _sync_results_miloto(self):
        """Sincroniza los resultados de MiLoto desde la web de Baloto."""
        base_url = 'https://baloto.com/miloto/resultados-miloto/'
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
                if numbers:
                    self.create({
                        'number_1': numbers[0],
                        'number_2': numbers[1],
                        'number_3': numbers[2],
                        'number_4': numbers[3],
                        'number_5': numbers[4],
                        'super_baloto': sorteo,
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

    @api.model
    def analyze_frequencies_pandas(self, option=None):
        _logger.info("Analyzing frequencies using pandas...")

        try:
            # Obtener los registros
            records = self.search_read(
                [("lottery_type_id.name", "=", option)],
                []
            )

            if not records:
                _logger.warning("No records found for analysis.")
                return []

            # Inicializar una lista para almacenar la información
            numbers_data = []

            # Recorrer cada registro para almacenar los números junto con la
            # fecha y el sorteo
            for record in records:
                for i in range(1, 6):  # Procesar number_1 a number_5
                    numbers_data.append({
                        'number': record.get(f'number_{i}'),
                        'draw_date': record.get('draw_date'),
                        'super_baloto': record.get('super_baloto')
                    })

            # Crear un DataFrame con los datos recolectados
            df = pd.DataFrame(numbers_data)

            # Convertir la columna 'draw_date' a formato datetime para extraer
            # el día de la semana
            df['draw_date'] = pd.to_datetime(df['draw_date'])
            df['day_of_week'] = df['draw_date'].dt.day_name()
            # Obtener el día de la semana

            # Concatenar la fecha, el día de la semana y el super_baloto en
            # un solo valor
            df['date_day_super'] = (
                df['draw_date'].dt.strftime('%Y-%m-%d') + ':' +
                df['day_of_week'] + ':' +
                df['super_baloto'].fillna('N/A').astype(str)
            )

            # Obtener la frecuencia de cada número
            frequency_df = df.groupby(
                'number'
            ).size().reset_index(name='frequency')

            # Agrupar las fechas (junto con el día y super_baloto) y sorteos
            # por número
            dates_sorteos_df = df.groupby('number').agg({
                'date_day_super': lambda x: list(x),
            }).reset_index()

            # Unir ambos DataFrames (frecuencia y detalles de fechas/sorteos)
            result_df = pd.merge(frequency_df, dates_sorteos_df, on='number')

            # Ordenar por la columna 'frequency' en orden descendente
            result_df = result_df.sort_values(by='frequency', ascending=False)

            # Convertir el resultado a una lista de diccionarios
            result = result_df.to_dict(orient='records')

            _logger.info("Frequencies analysis completed using pandas.")
            return result

        except Exception as e:
            _logger.error(f"Error during frequency analysis: {e}")
            return []

    @api.model
    def frequency_1_16_pandas(self, option):
        try:
            # Obtener los registros filtrados por tipo de lotería
            records = self.search_read(
                [("lottery_type_id.name", "=", option)],
                ['super_baloto', 'draw_date'],
            )

            if not records:
                _logger.warning("No records found for analysis.")
                return []

            # Lista para almacenar la información recolectada
            numbers_data = []

            # Recorrer cada registro y obtener el número junto con la fecha
            for record in records:
                numbers_data.append({
                    'number': record.get('super_baloto'),
                    'draw_date': record.get('draw_date')
                })

            # Crear un DataFrame con los datos recolectados
            df = pd.DataFrame(numbers_data)

            # Convertir la columna 'draw_date' a formato datetime
            df['draw_date'] = pd.to_datetime(df['draw_date'])

            # Crear una columna con el día de la semana (opcional)
            df['day_of_week'] = df['draw_date'].dt.day_name()

            # Concatenar la fecha y el día de la semana en un solo valor
            # (opcional)
            df['date_day_super'] = df[
                'draw_date'
            ].dt.strftime('%Y-%m-%d') + ':' + df['day_of_week']

            # Obtener la frecuencia de aparición de cada número
            frequency_df = df.groupby(
                'number'
            ).size().reset_index(name='frequency')

            # Agrupar las fechas por número y también obtener la fecha más
            # reciente
            dates_sorteos_df = df.groupby('number').agg({
                'date_day_super': lambda x: list(x),
                'draw_date': 'max'  # Obtener la fecha más reciente por número
            }).reset_index()

            # Unir los DataFrames de frecuencia y fechas
            result_df = pd.merge(frequency_df, dates_sorteos_df, on='number')

            # Ordenar los resultados por la columna 'draw_date' en orden
            # descendente
            result_df = result_df.sort_values(by='frequency', ascending=False)

            # Convertir el DataFrame en una lista de diccionarios
            result = result_df.to_dict(orient='records')

            _logger.info("Frequencies analysis completed using pandas.")
            return result

        except Exception as e:
            _logger.error(f"Error during frequency analysis: {e}")
            return []
