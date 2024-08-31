import os
import requests
import logging
from requests.exceptions import RequestException
from odoo import models, fields, api  # noqa: F401
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class FootballCountry(models.Model):
    _name = 'football.country'
    _description = 'Football Country'

    name = fields.Char(string='Name', required=True)
    country_code = fields.Char(
        string='Country Code',
    )
    flag = fields.Char(string='Flag')
    has_data = fields.Boolean(compute='_compute_has_data', store=True)
    session_ids = fields.One2many(
        comodel_name='football.session',
        inverse_name='country_id',
        string='Sessions'
    )

    @api.depends('name')
    def _compute_has_data(self):
        for record in self:
            record.has_data = len(self.search([])) > 0

    def _sync_countries(self):

        # Verifica si la tabla ya tiene datos
        if self.search([]):
            _logger.info('The countries data is already up-to-date.')
            # Opcional: Mostrar un mensaje al usuario en la interfaz
            raise UserError('The countries data is already up-to-date.')

        url = 'https://v3.football.api-sports.io/countries'
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            # # Levanta una excepción para códigos de error HTTP
            countries = response.json().get('response', [])
            for country in countries:
                self.create_or_update_country(country)

        except RequestException as e:
            # Manejo de excepciones relacionadas con la solicitud HTTP
            raise Exception(f"Error fetching countries from API: {str(e)}")

    def create_or_update_country(self, country_data):
        try:
            country = self.env['football.country'].search(
                [
                    ('country_code', '=', country_data['code']),
                    ('name', '=', country_data['name'])
                ], limit=1)
            if country:
                country.write({
                    'name': str(country_data['name']),
                    'flag': str(country_data['flag']),
                })
            else:
                self.env['football.country'].create({
                    'name': str(country_data['name']),
                    'country_code': str(country_data['code']),
                    'flag': str(country_data['flag']),
                })
        except Exception as e:
            # Manejo de cualquier otra excepción
            raise Exception(f"Error updating or creating country: {str(e)}")
