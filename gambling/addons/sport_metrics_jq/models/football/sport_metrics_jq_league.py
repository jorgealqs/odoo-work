import logging
import os
import requests  # type:ignore
from requests.exceptions import RequestException  # type:ignore
from odoo import models, fields, api

# Configuring the logger to record relevant information in Odoo logs
_logger = logging.getLogger(__name__)


class SportMetricsJQLeague(models.Model):
    _name = 'sport.metrics.jq.league'
    _description = 'SportMetricsJQ League'
    _order = "name desc"

    # Model fields
    id_league = fields.Integer(string='League ID', required=True)
    name = fields.Char(string='Name', required=True)
    type = fields.Char(string='Type')
    logo = fields.Char(string='Logo URL')
    start = fields.Date(string='Start Date')
    end = fields.Date(string='End Date')
    follow = fields.Boolean(string='Follow', default=False)
    # New fields
    country_id = fields.Many2one(
        'sport.metrics.jq.country',
        string='Country',
        required=True
    )
    continent = fields.Char(
        string='Continent',
        related='country_id.continent',
        store=True
    )
    session_id = fields.Many2one(
        'sport.metrics.jq.session',
        string='Session',
        required=True
    )
    # One2many relation to teams
    team_ids = fields.One2many(
        'sport.metrics.jq.team',
        'league_id',
        string='Teams'
    )
    # One2many relation to Standings
    standing_ids = fields.One2many(
        'sport.metrics.jq.standing',
        'league_id',
        string='Standings'
    )
    # One2many relation to Round
    round_ids = fields.One2many(
        'sport.metrics.jq.round',
        'league_id',
        string='Round'
    )

    # One2many relation to Round
    fixtures_ids = fields.One2many(
        'sport.metrics.jq.fixture',
        'league_id',
        string='Round'
    )

    filtered_fixtures_ids = fields.One2many(
        'sport.metrics.jq.fixture',
        compute='_compute_filtered_fixtures',
        string='Filtered Fixtures',
        store=False
    )

    @api.depends('fixtures_ids.date')
    def _compute_filtered_fixtures(self):
        today = fields.Date.today()
        # Obtiene solo la parte de la fecha, sin la hora
        for league in self:
            # Filtra los fixtures que tienen fecha igual a hoy
            league.filtered_fixtures_ids = league.fixtures_ids.filtered(
                lambda f: f.date.date() == today  # Compara solo la fecha
            )

    @api.onchange('fixtures_ids')
    def _onchange_fixtures(self):
        # Este método se llamará cada vez que se cambie fixtures_ids
        today = fields.Date.today()
        # Obtiene solo la parte de la fecha, sin la hora
        self.filtered_fixtures_ids = self.fixtures_ids.filtered(
            lambda f: f.date.date() == today  # Compara solo la fecha
        )

    def _sync_leagues(self, info=None):
        if info:
            leagues = self._fetch_leagues(info)
            if leagues:
                self._process_and_save_leagues(leagues, info)

    def _fetch_leagues(self, info=None):
        """Fetch leagues data from API for a given country and season."""
        country = info.get("country")
        session = info.get("session")
        country_code = info.get("country_code")
        _logger.info(
            f"Fetching leagues for {country} ({country_code}), season "
            f"{session}."
        )

        base_url = os.getenv('API_FOOTBALL_URL')
        url = (
            f'{base_url}/leagues?country={country}&season={session}'
            if country == 'World'
            else f'{base_url}/leagues?code={country_code}&season={session}'
        )

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
                f"Error fetching data from API for {country_code} and  "
                f"{session}: {e}"
            )
            return []

    def _process_and_save_leagues(self, leagues, info=None):
        """Process and save the fetched leagues data."""
        country_name = info.get('country')
        session_year = info.get('session')

        # Fetch country and session IDs in bulk
        country = self.env[
            'sport.metrics.jq.country'
        ].search([('name', '=', country_name)], limit=1)
        session = self.env[
            'sport.metrics.jq.session'
        ].search([('year', '=', session_year)], limit=1)

        if not country:
            _logger.error(f"Country '{country_name}' not found in the system.")
            return
        if not session:
            _logger.error(f"Session '{session_year}' not found in the system.")
            return

        # Bulk fetch all existing leagues to avoid searching for each league
        # individually
        existing_leagues = self.search(
            [
                (
                    'id_league',
                    'in',
                    [league.get('league').get('id') for league in leagues]
                ),
                ('country_id', '=', country.id),
                ('session_id', '=', session.id),
            ]
        )
        existing_league_ids = {league.id_league for league in existing_leagues}

        for league in leagues:
            league_data = league.get('league', {})
            league_id = league_data.get('id')
            seasons = league.get('seasons', [])

            if league_id not in existing_league_ids:
                for season in seasons:
                    data = {
                        'id_league': league_id,
                        'name': league_data.get('name'),
                        'type': league_data.get('type'),
                        'logo': league_data.get('logo'),
                        'start': season.get('start'),
                        'end': season.get('end'),
                        'country_id': country.id,
                        'session_id': session.id,
                    }
                    self.create(data)

    def sync_standigs(self):
        data = {
            "id_league_table": self.id,
            "id_league": self.id_league,
            "session": self.session_id.year,
            "id_session": self.session_id.id,
        }
        model_team = self.env['sport.metrics.jq.team']
        model_team._sync_teams(data)

        model_standing = self.env['sport.metrics.jq.standing']
        model_standing._sync_standing(data)

        model_round = self.env['sport.metrics.jq.round']
        model_round._sync_round(data)

        model_fixture = self.env['sport.metrics.jq.fixture']
        model_fixture._sync_fixture(data)
