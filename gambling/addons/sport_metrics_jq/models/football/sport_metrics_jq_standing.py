import os
import logging
import requests  # type:ignore
from datetime import datetime
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQTeamStanding(models.Model):
    _name = 'sport.metrics.jq.standing'
    _description = 'SportMetricsJQ Standing'
    _order = 'rank ASC'
    _rec_name = 'league_id'

    rank = fields.Integer(string='Rank', required=True)
    points = fields.Integer(string='Points', required=True)
    goals_diff = fields.Integer(string='Goal Difference')
    status = fields.Char(string='Status')
    description = fields.Char(string='Description')
    update = fields.Datetime(string='Last Update')

    # Relation FootballSession
    session_id = fields.Many2one(
        comodel_name='sport.metrics.jq.session',
        string='Session',
        required=True
    )

    # Relation FootballLeague
    league_id = fields.Many2one(
        comodel_name='sport.metrics.jq.league',
        string='League',
        required=True
    )

    # Relation FootballTeam
    team_id = fields.Many2one(
        comodel_name='sport.metrics.jq.team',
        string='Team',
        required=True,
    )

    # Relation to goals for home/away stats
    home_goals_id = fields.Many2one(
        'sport.metrics.jq.goals',
        string='Home Goals',
    )
    home_goals_id_played = fields.Integer(
        related='home_goals_id.played',
        string='Home Played'
    )
    home_goals_id_win = fields.Integer(
        related='home_goals_id.win',
        string='Home Win'
    )
    home_goals_id_draw = fields.Integer(
        related='home_goals_id.draw',
        string='Home Draw'
    )
    home_goals_id_lose = fields.Integer(
        related='home_goals_id.lose',
        string='Home Lose'
    )
    home_goals_id_goals_for = fields.Integer(
        related='home_goals_id.goals_for',
        string='Home goals for'
    )
    home_goals_id_goals_against = fields.Integer(
        related='home_goals_id.goals_against',
        string='Home goals against'
    )

    away_goals_id = fields.Many2one(
        'sport.metrics.jq.goals',
        string='Away Goals',
    )
    away_goals_id_played = fields.Integer(
        related='away_goals_id.played',
        string='Away Played'
    )
    away_goals_id_win = fields.Integer(
        related='away_goals_id.win',
        string='Away Win'
    )
    away_goals_id_draw = fields.Integer(
        related='away_goals_id.draw',
        string='Away Draw'
    )
    away_goals_id_lose = fields.Integer(
        related='away_goals_id.lose',
        string='Away Lose'
    )
    away_goals_id_goals_for = fields.Integer(
        related='away_goals_id.goals_for',
        string='Away goals for'
    )
    away_goals_id_goals_against = fields.Integer(
        related='away_goals_id.goals_against',
        string='Away goals against'
    )

    all_goals_id = fields.Many2one(
        'sport.metrics.jq.goals',
        string='Total Goals',
    )

    all_goals_id_played = fields.Integer(
        related='all_goals_id.played',
        string='Home Played'
    )
    all_goals_id_win = fields.Integer(
        related='all_goals_id.win',
        string='All stats Win'
    )
    all_goals_id_draw = fields.Integer(
        related='all_goals_id.draw',
        string='All stats Draw'
    )
    all_goals_id_lose = fields.Integer(
        related='all_goals_id.lose',
        string='All stats Lose'
    )
    all_goals_id_goals_for = fields.Integer(
        related='all_goals_id.goals_for',
        string='All stats goals for'
    )
    all_goals_id_goals_against = fields.Integer(
        related='all_goals_id.goals_against',
        string='All stats goals against'
    )

    def _sync_standing(self, data=None):
        id_league_table = data.get('id_league_table')
        id_league = data.get('id_league')
        session_year = data.get('session')
        id_session = data.get('id_session')
        base_url = os.getenv('API_FOOTBALL_URL')
        url = base_url + '/standings'
        headers = {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }
        params = {
            'league': id_league,
            'season': session_year
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json().get('response', [])
            for standings_data in data:
                league_data = standings_data.get('league', {})
                standings_data = league_data.get('standings', [[]])
                # Process each team in the standings
                for standings in standings_data:
                    for standing in standings:
                        team_data = standing.get('team', {})
                        team_id = team_data.get('id')
                        # Validate if this standing already exists for the
                        # team,
                        # league, and session
                        existing_standing = self.search([
                            ('team_id.id_team', '=', team_id),
                            ('league_id.id', '=', id_league_table),
                            ('session_id.id', '=', id_session),
                        ], limit=1)
                        if existing_standing:
                            # Update the existing standing
                            self._update_standing(existing_standing, standing)
                        else:
                            # Create a new standing
                            self._create_standing(
                                standing,
                                team_id,
                                id_league,
                                id_session,
                                id_league_table
                            )

        except requests.exceptions.HTTPError as http_err:
            _logger.error(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            _logger.error(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            _logger.error(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            _logger.error(f"Request error occurred: {req_err}")
        except Exception as e:
            _logger.error(f"An unexpected error occurred: {e}")

    def _create_standing(
            self,
            standing,
            team_id,
            league_id,
            id_session,
            id_league_table
    ):
        """Create a new standing record."""
        home_goals = self._create_or_update_goals(standing.get('home', {}))
        away_goals = self._create_or_update_goals(standing.get('away', {}))
        all_goals = self._create_or_update_goals(standing.get('all', {}))

        # Busca el equipo usando el id del equipo
        team_record = self.env['sport.metrics.jq.team'].search([
            ('id_team', '=', team_id),
            ('session_id', '=', id_session),
            ('league_id', '=', id_league_table),
        ], limit=1)

        if team_record:
            self.create({
                'rank': standing.get('rank'),
                'points': standing.get('points'),
                'goals_diff': standing.get('goalsDiff'),
                'status': standing.get('status'),
                'description': standing.get('description'),
                'update': self._convert_date(standing.get('update')),
                'team_id': team_record.id,
                'league_id': id_league_table,
                'session_id': id_session,
                'home_goals_id': home_goals.id,
                'away_goals_id': away_goals.id,
                'all_goals_id': all_goals.id,
            })
        else:
            _logger.error(
                f"Team record not found for team_id: {team_id}, league_id: "
                f"{league_id}, session_id: {id_session}"
            )

    def _update_standing(self, standing_record, standing):
        # Update home, away, and total goals
        standing_record.home_goals_id.write(
            self._prepare_goals_data(standing.get('home', {}))
        )
        standing_record.away_goals_id.write(
            self._prepare_goals_data(standing.get('away', {}))
        )
        standing_record.all_goals_id.write(
            self._prepare_goals_data(standing.get('all', {}))
        )

        # Update the standing record
        standing_record.write({
            'rank': standing.get('rank'),
            'points': standing.get('points'),
            'goals_diff': standing.get('goalsDiff'),
            'status': standing.get('status'),
            'description': standing.get('description'),
            'update': self._convert_date(standing.get('update')),
        })

    def _create_or_update_goals(self, goals_data):
        """
            Creates or updates the goals data in the sport.metrics.jq.goals
            model.
        """
        goals_values = self._prepare_goals_data(goals_data)
        return self.env['sport.metrics.jq.goals'].create(goals_values)

    def _prepare_goals_data(self, goals_data):
        """Prepares the data for goals (home, away, all)."""
        return {
            'played': goals_data.get('played', 0),
            'win': goals_data.get('win', 0),
            'draw': goals_data.get('draw', 0),
            'lose': goals_data.get('lose', 0),
            'goals_for': goals_data.get('goals', {}).get('for', 0),
            'goals_against': goals_data.get('goals', {}).get('against', 0),
        }

    def _convert_date(self, iso_date):
        """Convert ISO 8601 date format to the desired format."""
        if iso_date:
            try:
                return (
                    datetime
                    .fromisoformat(iso_date)
                    .strftime('%Y-%m-%d %H:%M:%S')
                )
            except ValueError as e:
                _logger.error(f"Date conversion error: {e}")
                return None
        return None
