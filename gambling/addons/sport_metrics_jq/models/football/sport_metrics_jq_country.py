import os
import requests  # type: ignore
import logging
from odoo import models, fields, api  # noqa: F401
from requests.exceptions import RequestException  # type: ignore

_logger = logging.getLogger(__name__)


class SportMetricsJQCountry(models.Model):
    _name = 'sport.metrics.jq.country'
    _description = 'SportMetricsJQ Country'
    _order = "name"

    name = fields.Char(string='Name', required=True)
    country_code = fields.Char(
        string='Country Code',
    )
    flag = fields.Char(string='Flag')
    continent = fields.Char(
        string='Continent',
        compute='_compute_continent',
        store=True
    )
    session = fields.Many2one(
        comodel_name='sport.metrics.jq.session',
        string='Sessions'
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
                        country.continent = 'World'
                except requests.RequestException:
                    country.continent = 'World'

    def sync_countries(self):
        base_url = os.getenv('API_FOOTBALL_URL')
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
            country = self.search(
                [
                    ('name', '=', country_data['name'])
                ], limit=1)
            if country:
                country.write({
                    'name': str(country_data['name']),
                    'flag': str(country_data['flag']),
                })
            else:
                self.create({
                    'name': str(country_data['name']),
                    'country_code': str(country_data['code']),
                    'flag': str(country_data['flag']),
                })
        except Exception as e:
            # Manejo de cualquier otra excepción
            raise Exception(f"Error updating or creating country: {str(e)}")

    def sync_leagues(self):
        data = {
            'country': self.name,
            'session': self.session.year,
            'country_code': self.country_code
        }
        model = self.env['sport.metrics.jq.league']
        model._sync_leagues(data)
