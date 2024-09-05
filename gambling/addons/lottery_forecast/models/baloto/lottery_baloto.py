import logging
import os
import pandas as pd
from datetime import datetime, timedelta
import random
import requests
import time
from bs4 import BeautifulSoup
from odoo import models, fields, tools
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

    def _sync_results(self):
        _logger.info("Iniciando sincronización de resultados con pandas")

        # Obtén la ruta del archivo dentro del módulo
        module_path = tools.config['addons_path'].split(',')[0]
        file_path = os.path.join(
            module_path,
            'lottery_forecast',
            'data_baloto',
            'baloto_results.xlsx'
        )

        try:
            # Leer el archivo XLSX usando pandas
            df = pd.read_excel(file_path)

            for _, row in df.iterrows():
                lottery_type_name = row['Type']
                numbers = [row[f'# {i}'] for i in range(1, 6)]
                super_baloto = row['Super Baloto']
                draw_date = row['Fecha de Creación']

                # Obtener el ID del tipo de lotería basado en el nombre
                lottery_type = self.env['lottery.baloto.type'].search(
                    [
                        ('name', '=', lottery_type_name)
                    ], limit=1
                )
                if not lottery_type:
                    _logger.warning(
                        f"Tipo de lotería '{lottery_type_name}' no encontrado."
                    )
                    continue

                # Buscar si ya existe un registro con la misma fecha
                existing_record = self.search([
                    ('draw_date', '=', draw_date),
                    ('lottery_type_id', '=', lottery_type.id)
                ], limit=1)
                if existing_record:
                    _logger.info(
                        f"Registro con la fecha {draw_date} ya existe. "
                        "Omite la creación."
                    )
                    continue

                # Crear nuevo registro
                self.create({
                    'number_1': numbers[0],
                    'number_2': numbers[1],
                    'number_3': numbers[2],
                    'number_4': numbers[3],
                    'number_5': numbers[4],
                    'super_baloto': super_baloto,
                    'draw_date': draw_date,
                    'lottery_type_id': lottery_type.id,
                })

            _logger.info("Sincronización completada con éxito")

            start_date = datetime(2021, 5, 1)
            end_date = datetime.now()

            dates = self._generate_dates(start_date, end_date)
            espera = random.uniform(10, 15)
            for date in dates:
                # Verificar si ya existe un registro para esta
                # fecha antes de hacer la petición
                existing_record = self.search(
                    [
                        ('draw_date', '=', date)
                    ], limit=1
                )
                if existing_record:
                    _logger.info(
                        f"Ya existe un registro para la fecha: {date}."
                    )
                else:
                    # Solo hacer la petición si no existe un registro
                    self._fetch_and_log_results(date)
                    time.sleep(espera)

        except Exception as e:
            _logger.error(f"Error al sincronizar resultados: {str(e)}")

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
        _logger.info(f"Procesando URL: {url}")

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
                        _logger.info(
                            f"Resultados guardados {tipos[idx]} fecha: {date}"
                        )
                    else:
                        _logger.warning(
                            f"Formato inesperado en los resultados: {row[2]}"
                        )
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

        # Iterar sobre el rango de sorteos para obtener los resultados
        for sorteo in range(1, 187):
            wait_time = random.uniform(10, 15)
            url = f'{base_url}{sorteo}'
            _logger.info(f"Accediendo a: {url}")

            try:
                lottery_type = self.env[
                    'lottery.baloto.type'
                ].search([('name', '=', 'MiLoto')], limit=1)
                if not lottery_type:
                    _logger.warning(
                        "Tipo de lotería 'MiLoto' no "
                        "encontrado. Omite el registro."
                    )
                    continue

                # Verificar si ya existe un registro con el mismo super_baloto
                existing_record = self.search([
                    ('super_baloto', '=', sorteo),
                    ('lottery_type_id', '=', lottery_type.id)
                ], limit=1)

                if existing_record:
                    _logger.info(
                        f"Ya existe un registro para el sorteo {sorteo}. "
                        "Se omite la sincronización."
                    )
                    continue

                # Realizar la petición HTTP a la página
                response = requests.get(url)
                response.raise_for_status()
                # Verificar que la petición fue exitosa

                soup = BeautifulSoup(response.content, 'html.parser')

                # Capturar la fecha del sorteo
                formatted_date = self._extract_date(soup, month_replacements)
                if not formatted_date:
                    _logger.warning(
                        f"No se pudo extraer la fecha para el sorteo {sorteo}"
                    )
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

                    _logger.info(
                        f"Fecha: {formatted_date}, "
                        f"Números capturados: {numbers}"
                    )
                else:
                    _logger.warning(
                        f"No se encontraron resultados para el sorteo {sorteo}"
                    )

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