import logging
import requests
import os
from odoo import models, fields
# from odoo.exceptions import RequestException

_logger = logging.getLogger(__name__)


class FootballTeam(models.Model):
    _name = 'football.team'
    _description = 'Football Team'
    _order = "name ASC"

    name = fields.Char(string='Name', required=True)
    id_team = fields.Integer(string='Team ID', required=True)
    code = fields.Char(string='Code')
    founded = fields.Integer(string='Founded Year')
    national = fields.Boolean(string='National')
    logo = fields.Char(string='Logo URL')

    # Relación con el modelo FootballVenue
    venue_id = fields.Many2one(
        comodel_name='football.venue',
        string='Venue'
    )

    # Relación con el modelo FootballLeague
    league_id = fields.Many2one(
        comodel_name='football.league',
        string='League'
    )

    # Relación con el modelo FootballSession
    session_id = fields.Many2one(
        comodel_name='football.session',
        string='Season'
    )

    # Relación con el modelo FootballCountry
    country_id = fields.Many2one(
        comodel_name='football.country',
        string='Country'
    )

    def _sync_teams(self):
        _logger.info('\n\nSync Teams started\n\n')

        active_leagues = self.env['football.league'].search([
            ('follow', '=', True),
        ])

        url = 'https://v3.football.api-sports.io/teams'
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

        for league in active_leagues:
            # Verificar si ya existen equipos para la
            # combinación de país, liga y sesión
            existing_teams = self.env['football.team'].search([
                ('league_id', '=', league.id),
                ('session_id', '=', league.session_id.id),
                ('country_id', '=', league.country_id.id)
            ])

            if existing_teams:
                _logger.info(
                    f"Teams already exist for League ID: "
                    f" {league.id_league}, Country: {league.country_id.name}, "
                    f"Year: {league.session_id.year}. Skipping API request."
                )
                continue

            # Realizar la petición a la API
            response = requests.get(url, headers=headers, params={
                'country': league.country_id.name,
                'league': league.id_league,
                'season': league.session_id.year,
            })

            if response.status_code == 200:
                data = response.json().get('response', [])
                for team_data in data:
                    venue_data = team_data.get('venue')
                    team_data_result = team_data.get('team')

                    # Validación y creación de Venue
                    venue = None
                    if venue_data and venue_data.get('name'):
                        venue = self.env['football.venue'].create({
                            'id_venue': venue_data.get('id'),
                            'name': venue_data.get('name'),
                            'address': venue_data.get('address', ''),
                            'city': venue_data.get('city', ''),
                            'capacity': venue_data.get('capacity', 0),
                            'surface': venue_data.get('surface', ''),
                            'image': venue_data.get('image', ''),
                        })
                    else:
                        _logger.warning(
                            f"Venue name missing for venue ID: "
                            f"{venue_data.get('id')}"
                        )

                    # Crear el equipo si se tiene un venue
                    if venue:
                        self.env['football.team'].create({
                            'name': team_data_result.get('name'),
                            'id_team': team_data_result.get('id'),
                            'code': team_data_result.get('code', ''),
                            'founded': team_data_result.get('founded', 0),
                            'national': team_data_result.get('national'),
                            'logo': team_data_result.get('logo', ''),
                            'venue_id': venue.id,
                            'league_id': league.id,
                            'session_id': league.session_id.id,
                            'country_id': league.country_id.id,
                        })
                        _logger.info(
                            f"Created team: {team_data_result.get('name')} "
                            f"with venue ID: {venue.id}"
                        )
            else:
                _logger.error(
                    f"Failed to fetch teams for League ID: {league.id_league},"
                    f"Country: {league.country_id.name}, Year: "
                    f" {league.session_id.year}. Status code: "
                    f"{response.status_code}")

        _logger.info('\n\nSync Teams completed\n\n')
