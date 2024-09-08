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

    def _sync_fixtures(self):
        """
        Synchronizes fixtures with the Football API for
        all leagues that are followed.
        """
        _logger.info("\nEntro1\n")

        football_leagues = self.env['football.league'].search(
            [
                ("follow", "=", True),
                # ("country_id.name", "=", "Argentina"),
            ]
        )

        if not football_leagues:
            _logger.info("No leagues found that are being followed.")
            return

        url = "https://v3.football.api-sports.io/fixtures"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

        for league in football_leagues:
            # Crear un diccionario para mapear team_id a Odoo team_id
            team_map = {
                team.id_team: {
                    'odoo_id': team.id,
                    'name': team.name
                }
                for team in league.team_ids
            }
            round_map = {
                round.name: round.id
                for round in league.session_round_ids
            }

            params = {
                'timezone': "America/Bogota",
                'league': league.id_league,
                'season': league.session_id.year,
            }
            try:
                _logger.info("\nEntro2 \n")
                # Realiza la solicitud GET a la API
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()
                fixtures = data.get('response', [])

                for fixture in fixtures:
                    # Obtener el round_name y buscar su ID en Odoo
                    round_name = fixture.get('league', {}).get('round')
                    round_id = round_map.get(round_name)

                    fixture_data = {
                        'league_id': league.id,
                        'fixture': fixture.get('fixture', {}),
                        'teams': fixture.get('teams', {}),
                        'goals': fixture.get('goals', {}),
                        'score': fixture.get('score', {}),
                        'round_id': round_id,
                        # Solo asignar el ID, no el diccionario
                    }
                    _logger.info("\nEntro 3\n")
                    self._create_or_update_fixture(fixture_data, team_map)

            except requests.RequestException as e:
                _logger.error(
                    f"An error occurred while fetching fixtures: {e}"
                )

    def _create_or_update_fixture(self, fixture_data, team_map):
        """
        Crea o actualiza un fixture basado en los datos proporcionados.
        """
        get_fixture = fixture_data.get('fixture', {})
        fixture_id = get_fixture.get('id')

        existing_fixture = self.env['football.fixture'].search(
            [('fixture_id', '=', fixture_id)], limit=1
        )

        home_team_api_id = (
            fixture_data.get('teams', {}).get('home', {}).get('id')
        )
        away_team_api_id = (
            fixture_data.get('teams', {}).get('away', {}).get('id')
        )

        if home_team_api_id:
            home_team_api_id = int(home_team_api_id)
        if away_team_api_id:
            away_team_api_id = int(away_team_api_id)

        home_team_odoo_data = team_map.get(home_team_api_id)
        away_team_odoo_data = team_map.get(away_team_api_id)

        _logger.info(
            f"\nHome team data from map: {home_team_odoo_data}\n"
            f"\nAway team data from map: {away_team_odoo_data}\n"
        )

        home_team_odoo_id = (
            home_team_odoo_data['odoo_id'] if home_team_odoo_data else None
        )
        away_team_odoo_id = (
            away_team_odoo_data['odoo_id'] if away_team_odoo_data else None
        )

        _logger.info(
            f"\nOdoo id home: {home_team_odoo_id}\n"
            f"\nOdoo id away: {away_team_odoo_id}\n"
        )

        # Convertir la fecha de la API al formato de Odoo
        match_date = get_fixture.get('date')
        try:
            # Convierte la fecha con el formato adecuado
            match_date = (
                datetime.strptime(match_date[:-6], '%Y-%m-%dT%H:%M:%S')
            )
        except ValueError as e:
            _logger.error(f"\n\nError converting date: {e}\n\n")
            return  # Si falla la conversión, no continuar

        if existing_fixture:
            _logger.info(f"Updating existing fixture: {fixture_id}")
        else:
            if not home_team_odoo_id or not away_team_odoo_id:
                if not home_team_odoo_id:
                    _logger.warning(
                        f"Cannot create fixture {fixture_id}: "
                        f"Home team ID {home_team_api_id} not found."
                    )
                if not away_team_odoo_id:
                    _logger.warning(
                        f"Cannot create fixture {fixture_id}: "
                        f"Away team ID {away_team_api_id} not found."
                    )
                return
            round_id = fixture_data.get('round_id')
            data = {
                "fixture_id": fixture_id,
                "referee": get_fixture.get('referee'),
                "date": match_date,
                "league_id": fixture_data.get('league_id'),
                "home_team_id": home_team_odoo_id,
                "away_team_id": away_team_odoo_id,
                "home_goals": fixture_data.get('goals', {}).get('home', 0),
                "away_goals": fixture_data.get('goals', {}).get('away', 0),
                "round_id": (
                    round_id
                    if isinstance(round_id, int) else round_id['odoo_id']
                ),  # Solo el ID

            }
            _logger.info(f"Creating new fixture: {data}")
            self.env['football.fixture'].create(data)
