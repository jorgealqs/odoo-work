import os
import requests
import logging
from requests.exceptions import RequestException
from odoo import models, fields, api  # noqa: F401

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
    has_active_session = fields.Boolean(
        string='Has Active Session',
        compute='_compute_has_active_session',
        store=True
    )
    continent = fields.Char(
        string='Continent',
        compute='_compute_continent',
        store=True
    )

    @api.depends('country_code')
    def _compute_continent(self):
        for country in self:
            if country.country_code:
                try:
                    response = requests.get(
                        f"https://restcountries.com/v3.1/alpha/"
                        f"{country.country_code}"
                    )
                    if response.status_code == 200:
                        data = response.json()
                        country.continent = data[0]['continents'][0]
                    else:
                        country.continent = 'Unknown'
                except requests.RequestException:
                    country.continent = 'Unknown'

    @api.depends('session_ids.is_active')
    def _compute_has_active_session(self):
        for country in self:
            country.has_active_session = any(
                session.is_active for session in country.session_ids
            )

    @api.depends('name')
    def _compute_has_data(self):
        for record in self:
            record.has_data = len(self.search([])) > 0

    def _sync_countries(self):
        # Verificar si la URL está correctamente configurada
        base_url = os.getenv('API_FOOTBALL_URL')
        if not base_url:
            raise Exception(
                "API_FOOTBALL_URL is not defined. Please configure "
                "the environment variable."
            )
        url = base_url + '/countries'
        headers = {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
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
