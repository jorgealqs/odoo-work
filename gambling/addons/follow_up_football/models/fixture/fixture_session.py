import logging
import requests
import os
# import time
from odoo import models, fields, api  # noqa: F401

_logger = logging.getLogger(__name__)


class FootballFixtureSessionRound(models.Model):
    _name = 'football.fixture.session.round'
    _description = 'Football Fixture Session'
    # _order = 'name ASC'

    name = fields.Char(string='Round Name', required=True)
    league_id = fields.Many2one(
        comodel_name='football.league',
        string='League',
        required=True
    )

    def _sync_rounds(self, id_league=None):
        """Sync fixture sessions (rounds) for leagues that are followed."""
        football_leagues = self._get_followed_leagues(id_league)

        if football_leagues:
            for league in football_leagues:
                try:
                    rounds_data = self._fetch_rounds_data(league)
                    self._process_rounds(league, rounds_data)
                except Exception as e:
                    _logger.error(
                        "Failed to sync rounds for league "
                        f"{league.id_league}: {e}"
                    )

    def _get_followed_leagues(self, id_league=None):
        """Retrieve leagues marked to be followed."""
        query = [("follow", "=", True)]
        if id_league:
            query.append(("id_league", "=", id_league))

        # Buscar ligas seguidas o la liga específica
        return self.env['football.league'].search(query)

    def _fetch_rounds_data(self, league):
        """Fetch rounds data from the API for a given league."""
        url = "https://v3.football.api-sports.io/fixtures/rounds"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }
        params = {
            'league': league.id_league,
            'season': league.session_id.year
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('response', [])

    def _process_rounds(self, league, rounds_data):
        """Process and store rounds data."""
        for round_name in rounds_data:
            if not self._round_exists(league.id, round_name):
                self._create_round(league.id, round_name)
                _logger.info(
                    f"Created round {round_name} for league {league.name}"
                )

    def _rounds_already_synced(self, league):
        """Check if any rounds are already synced for a given league."""
        existing_rounds = self.env['football.fixture.session.round'].search([
            ('league_id', '=', league.id),
        ])
        # Return True if there are already synced rounds for this league
        return bool(existing_rounds)

    def _round_exists(self, league_id, round_name):
        """Check if a round already exists."""
        return self.env['football.fixture.session.round'].search([
            ('name', '=', round_name),
            ('league_id', '=', league_id)
        ], limit=1)

    def _create_round(self, league_id, round_name):
        """Create a new round record."""
        self.env['football.fixture.session.round'].create({
            'name': round_name,
            'league_id': league_id,
        })

    def action_view_rounds(self):
        """Open the rounds related to the selected league."""
        self.ensure_one()  # Asegura que solo se seleccione una liga

        return {
            'type': 'ir.actions.act_window',
            'name': f"Fixtures for {self.name}",
            'view_mode': 'tree,form',
            'res_model': 'football.fixture',
            'domain': [
                ('round_id', '=', self.id),
                ('league_id', '=', self.league_id.id)
            ],  # Filtra por la ronda y la liga seleccionada
            'context': dict(self.env.context),
        }
