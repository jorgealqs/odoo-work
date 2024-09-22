import os
import logging
import requests
from requests.exceptions import RequestException
from odoo import models, fields
from odoo.exceptions import UserError

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
    # Relación inversa con los fixtures
    fixture_ids = fields.One2many(
        comodel_name='football.fixture',
        inverse_name='league_id',
        string='Fixtures'
    )
    continent = fields.Char(
        string='Continent',
        related='country_id.continent',
        store=True
    )

    def _sync_leagues(self, country_option=None):
        """
        Sync football leagues for active countries and
        their active sessions.
        """
        query = [('session_ids.is_active', '=', True)]
        if country_option:
            query.append(('name', '=', country_option))
        active_countries = self.env['football.country'].search(query)

        # Validación: Si no hay países activos, lanzar un mensaje de error
        if not active_countries:
            raise UserError("No active countries found with active sessions.")

        for country in active_countries:
            active_sessions = country.session_ids.filtered('is_active')
            sessions_info = [
                {'ID': session.id, 'Year': session.year}
                for session in active_sessions
            ]
            for session in sessions_info:
                leagues = self._fetch_leagues(
                    country.country_code,
                    session['Year'],
                    country_option
                )
                if leagues:
                    self._process_and_save_leagues(
                        leagues,
                        session['ID'],
                        country.id
                    )

    def _fetch_leagues(self, country_code, year, country_option=None):
        """Fetch leagues data from API for a given country and season."""
        base_url = os.getenv('API_FOOTBALL_URL')
        if not base_url:
            raise Exception(
                "API_FOOTBALL_URL is not defined. Please configure "
                "the environment variable."
            )
        if (country_option and country_option == 'World'):
            url = base_url + f'/leagues?country={country_option}&season={year}'
        else:
            url = base_url + f'/leagues?code={country_code}&season={year}'
        headers = {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json().get('response', [])
        except RequestException as e:
            _logger.error(
                f"Error fetching data from API for {country_code} "
                f"and {year}: {e}"
            )
            return []

    def _process_and_save_leagues(self, leagues, session_id, country_id):
        """Process and save the fetched leagues data."""
        for league in leagues:
            league_data = league.get('league', {})
            seasons = league.get('seasons', [])
            for season in seasons:
                data = {
                    'id_league': league_data.get('id'),
                    'name': league_data.get('name'),
                    'type': league_data.get('type'),
                    'logo': league_data.get('logo'),
                    'session_id': session_id,
                    'country_id': country_id,
                    'start': season.get('start'),
                    'end': season.get('end')
                }
                # Check if league already exists in the database
                existing_league = self.env['football.league'].search([
                    ('id_league', '=', league_data.get('id')),
                    ('session_id', '=', session_id),
                    ('country_id', '=', country_id)
                ], limit=1)

                if not existing_league:
                    # Create new league if it does not exist
                    self.env['football.league'].create(data)

    def update_standings_by_league(self):

        # # Guardar en el log, buscar la forma de que solo se ejeucate una vez
        # por dia
        # self.env['ir.logging'].create({
        #     'name': 'update_standings_by_league',
        #     'type': 'server',
        #     'dbname': self._cr.dbname,
        #     'level': 'info',
        #     'message': f'Update_standings_by_league fue ejecutada en '
        #     f'{datetime.now()}',
        #     'path': __file__,
        #     'line': 'N/A',
        #     'func': 'update_standings_by_league',
        # })

        country_id = self.country_id
        id_league = self.id_league
        model_football_standing = self.env['football.standing']
        model_football_standing._sync_standings(country_id.name, id_league)
        # return {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Éxito',
        #         'message': 'Updated standings.',
        #         'type': 'success',  # También puede ser 'warning' o 'info'
        #         'sticky': False,
        #         # Si es True, la notificación permanecerá hasta que el
        # usuario
        #         # la cierre
        #     }
        # }
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # Esto recargará la vista
        }

    def update_fixtures_by_league(self):
        id_league = self.id_league
        model_football_fixture = self.env['football.fixture']
        model_football_fixture._sync_fixtures(id_league)
        # Notificación de éxito
        # notification_action = {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': 'Éxito',
        #         'message': 'Updated fixtures.',
        #         'type': 'success',
        #         'sticky': False,
        #     }
        # }

        # Retornar acción para recargar la vista actual
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # Esto recargará la vista
        }

    def update_teams_by_league(self):
        id_league = self.id_league
        model_football_team = self.env['football.team']
        model_football_team._sync_teams(id_league)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',  # Esto recargará la vista
        }
