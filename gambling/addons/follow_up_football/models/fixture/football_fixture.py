import logging
import os
import requests
from datetime import datetime
from odoo import models, fields

_logger = logging.getLogger(__name__)


class FootballFixture(models.Model):
    _name = 'football.fixture'
    _description = 'Football Fixture'
    _order = 'date DESC'

    # Información del partido (fixture)
    fixture_id = fields.Integer(string='Fixture ID', required=True)
    referee = fields.Char(string='Referee')
    date = fields.Datetime(string='Match Date', required=True)
    # Goles anotados
    home_goals = fields.Integer(string='Home Team Goals')
    away_goals = fields.Integer(string='Away Team Goals')

    # Relación con la liga y temporada
    league_id = fields.Many2one(
        comodel_name='football.league',
        string='League',
        required=True
    )

    # Relación con el round de la liga
    round_id = fields.Many2one(
        comodel_name='football.fixture.session.round',
        string='Round',
        required=True  # Si es obligatorio o no
    )

    # Equipos que juegan el partido
    home_team_id = fields.Many2one(
        comodel_name='football.team',
        string='Home Team',
        required=True
    )
    away_team_id = fields.Many2one(
        comodel_name='football.team',
        string='Away Team',
        required=True
    )

    # Relación con el modelo Score para almacenar los
    # resultados de cada fase del partido
    score_id = fields.Many2one(
        comodel_name='football.fixture.score',
        string='Score'
    )
    country_id = fields.Many2one(
        comodel_name='football.country',
        string='Country',
        related='league_id.country_id',
        store=True,
        # Puedes almacenar el valor en la base de datos si es necesario
    )

    def _sync_fixtures(self):
        """
        Synchronizes fixtures with the Football API for all leagues that
        are followed.
        """

        # Obtener ligas que se están siguiendo
        football_leagues = self._get_followed_leagues()

        if not football_leagues:
            _logger.warning("No leagues found that are being followed.")
            return

        headers = self._get_api_headers()
        for league in football_leagues:
            self._sync_league_fixtures(league, headers)

    def _get_followed_leagues(self):
        """
        Retrieve the football leagues that are being followed.
        """
        return self.env['football.league'].search(
            [
                ("follow", "=", True),
                # ("country_id.name", "in", ['Brazil']),
            ]
        )

    def _get_api_headers(self):
        """
        Retrieve API headers for the Football API.
        """
        return {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

    def _sync_league_fixtures(self, league, headers):
        """
        Sync the fixtures for a specific league.
        """
        base_url = os.getenv('API_FOOTBALL_URL')
        url = f"{base_url}/fixtures"

        params = self._get_league_api_params(league)
        team_map = self._get_team_map(league)
        round_map = self._get_round_map(league)

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            fixtures = data.get('response', [])
            _logger.info(
                f"Syncing {len(fixtures)} fixtures for league {league.name}"
            )

            for fixture in fixtures:
                self._process_fixture(fixture, league, team_map, round_map)
        except requests.RequestException as e:
            _logger.error(f"An error occurred while fetching fixtures: {e}")

    def _get_league_api_params(self, league):
        """
        Build the API parameters for the league.
        """
        return {
            'timezone': "America/Bogota",
            'league': league.id_league,
            'season': league.session_id.year,
        }

    def _get_team_map(self, league):
        """
        Create a mapping between team API IDs and Odoo IDs for a
        specific league.
        """
        return {
            team.id_team: {'odoo_id': team.id, 'name': team.name}
            for team in league.team_ids
        }

    def _get_round_map(self, league):
        """
        Create a mapping between round names and their Odoo IDs for a
        specific league.
        """
        return {round.name: round.id for round in league.session_round_ids}

    def _process_fixture(self, fixture, league, team_map, round_map):
        """
        Process a single fixture and create or update it in Odoo.
        """
        round_id = round_map.get(fixture.get('league', {}).get('round'))
        fixture_data = {
            'league_id': league.id,
            'fixture': fixture.get('fixture', {}),
            'teams': fixture.get('teams', {}),
            'goals': fixture.get('goals', {}),
            'score': fixture.get('score', {}),
            'round_id': round_id,
        }
        self._create_or_update_fixture(fixture_data, team_map)

    def _create_or_update_fixture(self, fixture_data, team_map):
        """
        Create or update a fixture based on the API data.
        """
        fixture_id = fixture_data['fixture'].get('id')
        existing_fixture = self.env[
            'football.fixture'
        ].search(
            [
                ('fixture_id', '=', fixture_id)
            ], limit=1
        )

        # Obtener los equipos desde el team_map
        home_team_id = self._get_team_odoo_id(
            fixture_data['teams'].get('home', {}).get('id'),
            team_map
        )
        away_team_id = self._get_team_odoo_id(
            fixture_data['teams'].get('away', {}).get('id'),
            team_map
        )

        if not home_team_id or not away_team_id:
            _logger.warning(
                f"Fixture {fixture_id} missing team data: {fixture_data}, "
                f"home_team_id={home_team_id}, away_team_id={away_team_id}"
            )
            return

        match_date = self._parse_api_date(fixture_data['fixture'].get('date'))

        if not match_date:
            _logger.warning(f"Invalid match date for fixture {fixture_id}")
            return

        data = self._build_fixture_data(
            fixture_data,
            home_team_id,
            away_team_id,
            match_date
        )

        if existing_fixture:
            _logger.info(f"Updating fixture {fixture_id}")
            existing_fixture.write(data)
        else:
            _logger.info(f"Creating fixture {fixture_id}")
            self.env['football.fixture'].create(data)

    def _get_team_odoo_id(self, api_team_id, team_map):
        """
        Retrieve the Odoo team ID from the API team ID using the team map.
        """
        team_data = team_map.get(api_team_id)
        return team_data['odoo_id'] if team_data else None

    def _parse_api_date(self, api_date):
        """
        Parse the fixture date from the API format.
        """
        try:
            return datetime.strptime(api_date[:-6], '%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            _logger.error(f"Error parsing date: {e}")
            return None

    def _build_fixture_data(
            self,
            fixture_data,
            home_team_id,
            away_team_id,
            match_date
    ):
        """
        Build the fixture data dictionary for creation or update.
        """
        return {
            "fixture_id": fixture_data['fixture'].get('id'),
            "referee": fixture_data['fixture'].get('referee'),
            "date": match_date,
            "league_id": fixture_data['league_id'],
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "home_goals": fixture_data.get('goals', {}).get('home', 0),
            "away_goals": fixture_data.get('goals', {}).get('away', 0),
            "round_id": fixture_data['round_id'],
        }
