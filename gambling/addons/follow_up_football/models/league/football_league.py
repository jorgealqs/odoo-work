import os
import logging
import requests
from odoo import models, fields

_logger = logging.getLogger(__name__)


class FootballLeague(models.Model):
    _name = 'football.league'
    _description = 'Football League'
    _order = "name ASC"

    # Fields based on the API response
    id_league = fields.Integer(string='League ID', required=True)
    name = fields.Char(string='Name', required=True)
    type = fields.Char(string='Type')
    logo = fields.Char(string='Logo URL')
    # Many2one relationship to the football.session model
    session_id = fields.Many2one(
        comodel_name='football.session',
        string='Season',
        required=True
    )
    # Campo relacionado
    season_year = fields.Char(
        related='session_id.year',
        string='Session',
        store=True
    )
    # Many2one relationship to the football.country model
    country_id = fields.Many2one(
        comodel_name='football.country',
        string='Country',
        required=True
    )
    start = fields.Date(string='Start Date')
    end = fields.Date(string='End Date')
    # New boolean field to indicate if the league should be followed
    follow = fields.Boolean(string='Follow', default=False)
    # Relación One2many con el modelo FootballTeam
    team_ids = fields.One2many(
        comodel_name='football.team',
        inverse_name='league_id',
        string='Teams'
    )
    # Relación One2many con el modelo FootballStanding
    standing_ids = fields.One2many(
        comodel_name='football.standing',
        inverse_name='league_id',
        string='Standings'
    )
    session_round_ids = fields.One2many(
        comodel_name='football.fixture.session.round',
        inverse_name='league_id',
        string='Session Rounds'
    )

    def _sync_leagues(self):
        active_countries = self.env['football.country'].search([
            ('session_ids.is_active', '=', True)
        ])
        # Iterar sobre los países activos y registrar información
        for country in active_countries:
            # Filtrar sesiones activas para el país
            active_sessions = country.session_ids.filtered('is_active')
            # Construir la lista de sesiones activas con ID y Year
            sessions_info = [
                {'ID': session.id, 'Year': session.year}
                for session in active_sessions
            ]
            # Imprimir información de cada sesión
            for session in sessions_info:

                # Verificar si ya existen registros para el país y la sesión
                existing_leagues = self.env['football.league'].search([
                    ('country_id', '=', country.id),
                    ('session_id', '=', session['ID'])
                ])

                if existing_leagues:
                    _logger.info(
                        f"\n Ya existen datos para el país "
                        f"{country.name} y la temporada "
                        f"{session['Year']}. Omitting API request.\n\n"
                    )
                    continue  # Pasar al siguiente país/sesión

                url = (
                    "https://v3.football.api-sports.io/leagues"
                    f"?code={country.country_code}&season={session['Year']}"
                )
                headers = {
                    'x-rapidapi-host': 'v3.football.api-sports.io',
                    'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
                }
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status()
                    # Lanza una excepción para
                    # códigos de estado HTTP no exitosos

                    data = response.json()
                    leagues = data.get('response', [])

                    # Procesar y guardar las ligas obtenidas
                    for league in leagues:
                        league_data = league.get('league', {})
                        seasons = league.get('seasons', [])
                        for season in seasons:
                            data = {
                                'id_league': league_data.get('id'),
                                'name': league_data.get('name'),
                                'type': league_data.get('type'),
                                'logo': league_data.get('logo'),
                                'session_id': session['ID'],
                                'country_id': country.id,
                                'start': season.get('start'),
                                'end': season.get('end')
                            }
                            self.env['football.league'].create(data)
                            _logger.info(f"\n\n league created: {data} \n\n")
                except requests.RequestException as e:
                    _logger.error(
                        f"Error al obtener datos de la API "
                        f"para {country.country_code} "
                        f"y {session['Year']}: {e}")

    def donwload_fixtures_round(self):
        _logger.info("\n\ndonwload_fixtures_round\n\n")
