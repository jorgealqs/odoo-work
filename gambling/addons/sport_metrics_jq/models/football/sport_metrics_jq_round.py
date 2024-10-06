import logging
import requests
import os
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQRound(models.Model):
    _name = 'sport.metrics.jq.round'
    _description = 'SportMetricsJQ Round'
    _order = "name ASC"

    name = fields.Char(string='Round Name', required=True)
    league_id = fields.Many2one(
        comodel_name='sport.metrics.jq.league',
        string='League',
        required=True
    )
    session_id = fields.Many2one(
        'sport.metrics.jq.session',
        string='Session',
        required=True
    )

    def _sync_round(self, data=None):
        id_league_table = data.get('id_league_table')
        id_league = data.get('id_league')
        session = data.get('session')
        id_session = data.get('id_session')
        rounds_data = self._fetch_rounds_data(id_league, session)
        self._process_rounds(id_league_table, id_session, rounds_data)

    def _process_rounds(self, id_league_table, id_session, rounds_data):
        """Process and store rounds data."""
        for round_name in rounds_data:
            if not self._round_exists(id_league_table, id_session, round_name):
                self._create_round(id_league_table, id_session, round_name)
                _logger.info(
                    f"Created round {round_name}"
                )

    def _create_round(self, id_league_table, id_session, round_name):
        """Create a new round record."""
        self.create({
            'name': round_name,
            'league_id': id_league_table,
            'session_id': id_session
        })

    def _round_exists(self, id_league_table, id_session, round_name):
        """Check if a round already exists."""
        return self.search([
            ('name', '=', round_name),
            ('league_id', '=', id_league_table),
            ('session_id', '=', id_session)
        ], limit=1)

    def _fetch_rounds_data(self, id_league=None, session=None):
        """Fetch rounds data from the API for a given league."""
        url = "https://v3.football.api-sports.io/fixtures/rounds"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }
        params = {
            'league': id_league,
            'season': session
        }

        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get('response', [])

    def action_view_rounds(self):
        """Open the rounds related to the selected league."""
        self.ensure_one()  # Asegura que solo se seleccione una liga

        return {
            'type': 'ir.actions.act_window',
            'name': f"Fixtures for {self.name}",
            'view_mode': 'tree,form',
            'res_model': 'sport.metrics.jq.fixture',
            'domain': [
                ('round_id', '=', self.id),
                ('league_id', '=', self.league_id.id),
                ('session_id', '=', self.session_id.id)
            ],
            'context': dict(self.env.context),
        }
