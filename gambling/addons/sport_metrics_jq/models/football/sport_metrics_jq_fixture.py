import logging
import os
import requests
from datetime import datetime
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQFixture(models.Model):
    _name = 'sport.metrics.jq.fixture'
    _description = 'SportMetricsJQ Fixture'
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
        comodel_name='sport.metrics.jq.league',
        string='League',
        required=True
    )

    # Relación con el round de la liga
    round_id = fields.Many2one(
        comodel_name='sport.metrics.jq.round',
        string='Round',
        required=True  # Si es obligatorio o no
    )

    session_id = fields.Many2one(
        'sport.metrics.jq.session',
        string='Session',
        required=True
    )

    # Equipos que juegan el partido
    home_team_id = fields.Many2one(
        comodel_name='sport.metrics.jq.team',
        string='Home Team',
        required=True
    )
    away_team_id = fields.Many2one(
        comodel_name='sport.metrics.jq.team',
        string='Away Team',
        required=True
    )

    # Relación con el modelo Score para almacenar los
    # resultados de cada fase del partido
    score_id = fields.Many2one(
        comodel_name='sport.metrics.jq.score',
        string='Score'
    )

    country_id = fields.Many2one(
        related='league_id.country_id',
        string='Country',
        store=True  # Almacenar este campo en la base de datos
    )

    # Relation with sport.metrics.jq.prediction
    prediction_ids = fields.One2many(
        comodel_name='sport.metrics.jq.prediction',
        inverse_name='fixture_id',
        string='Predictions'
    )

    # Relation with sport.metrics.jq.prediction.teams
    prediction_team_home_ids = fields.One2many(
        comodel_name='sport.metrics.jq.prediction.teams',
        string='Predictions home',
        inverse_name='fixture_id',
    )

    prediction_team_away_ids = fields.One2many(
        comodel_name='sport.metrics.jq.prediction.teams',
        string='Predictions away',
        inverse_name='fixture_id',
    )

    # One-to-one relationship with prediction comparison
    prediction_comparison_id = fields.One2many(
        comodel_name='sport.metrics.jq.prediction.comparison',
        string='Prediction Comparison',
        inverse_name='fixture_id',
    )

    def _sync_fixture(self, dataInfo=None):
        headers = self._get_api_headers()
        self._sync_league_fixtures(dataInfo, headers)

    def _sync_league_fixtures(self, dataInfo, headers):
        """
        Sync the fixtures for a specific league.
        """
        base_url = os.getenv('API_FOOTBALL_URL')
        url = f"{base_url}/fixtures"
        params = self._get_league_api_params(dataInfo)
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            fixtures = data.get('response', [])
            for fixture in fixtures:
                self._process_fixture(fixture, dataInfo)
        except requests.RequestException as e:
            _logger.error(f"An error occurred while fetching fixtures: {e}")

    def _process_fixture(self, fixture, dataInfo):
        """
        Process a single fixture and create or update it in Odoo.
        """
        round = fixture.get('league', {}).get('round', 0)

        round_id = self.env['sport.metrics.jq.round'].search_read(
            [
                ("name", "=", round),
                ("league_id", "=", dataInfo.get('id_league_table')),
                ("session_id", "=", dataInfo.get('id_session')),
            ], limit=1
        )

        fixture_data = {
            'league_id': dataInfo.get('id_league_table'),
            'fixture': fixture.get('fixture', {}),
            'teams': fixture.get('teams', {}),
            'goals': fixture.get('goals', {}),
            'score': fixture.get('score', {}),
            'round_id': round_id,
            'session_id': dataInfo.get('id_session'),
        }
        self._create_or_update_fixture(fixture_data, dataInfo)

    def _create_or_update_fixture(self, fixture_data, dataInfo):
        """
        Create or update a fixture based on the API data.
        """
        fixture_id = fixture_data['fixture'].get('id')
        existing_fixture = self.search(
            [
                ('fixture_id', '=', fixture_id)
            ], limit=1
        )
        # Obtener los equipos desde el team_map
        home_team_id = fixture_data['teams'].get('home', {}).get('id')
        away_team_id = fixture_data['teams'].get('away', {}).get('id')
        model_home_team_id = self.env['sport.metrics.jq.team'].search(
            [
                ("id_team", "=", home_team_id),
                ("session_id.id", "=", dataInfo.get('id_session')),
                ("league_id.id", "=", dataInfo.get('id_league_table')),
            ], limit=1
        )
        home_team_id = model_home_team_id.id if model_home_team_id else False

        model_away_team_id = self.env['sport.metrics.jq.team'].search(
            [
                ("id_team", "=", away_team_id),
                ("session_id.id", "=", dataInfo.get('id_session')),
                ("league_id.id", "=", dataInfo.get('id_league_table')),
            ], limit=1
        )
        away_team_id = (
            model_away_team_id.id if model_away_team_id else False
        )

        if not home_team_id or not away_team_id:
            _logger.warning(
                f"\n\nError Fixture {fixture_id} \n\n"
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
            self.create(data)

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
            "round_id": (
                fixture_data['round_id'][0]['id']
                if fixture_data['round_id'] else False
            ),  # Updated line
            'session_id': fixture_data['session_id']
        }

    def _get_api_headers(self):
        """
        Retrieve API headers for the Football API.
        """
        return {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

    def _get_league_api_params(self, data):
        """
        Build the API parameters for the league.
        """
        return {
            'timezone': "America/Bogota",
            'league': data.get('id_league'),
            'season': data.get('session'),
        }

    def _parse_api_date(self, api_date):
        """
        Parse the fixture date from the API format.
        """
        try:
            return datetime.strptime(api_date[:-6], '%Y-%m-%dT%H:%M:%S')
        except ValueError as e:
            _logger.error(f"Error parsing date: {e}")
            return None

    def sync_predictions(self):
        data = {
            'fixture_id_table': self.id,
            'fixture_id': self.fixture_id,
            'league_id': self.league_id.id,
            'session_id': self.session_id.id,
        }
        model_prediction = self.env['sport.metrics.jq.prediction']
        model_prediction._sync_predictions(**data)
