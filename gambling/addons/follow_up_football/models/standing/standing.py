import logging
import os
import requests
from odoo import models, fields
from datetime import datetime

_logger = logging.getLogger(__name__)


class FootballStanding(models.Model):
    _name = 'football.standing'
    _description = 'Football Standing'
    _order = 'rank ASC'

    rank = fields.Integer(string='Rank', required=True)
    points = fields.Integer(string='Points', required=True)
    goals_diff = fields.Integer(string='Goal Difference')
    status = fields.Char(string='Status')
    description = fields.Char(string='Description')
    update = fields.Datetime(string='Last Update')

    # Relación con FootballSession
    session_id = fields.Many2one(
        comodel_name='football.session',
        string='Session',
        required=True
    )

    # Relación con FootballLeague
    league_id = fields.Many2one(
        comodel_name='football.league',
        string='League',
        required=True
    )

    # Relación con FootballTeam utilizando id_team
    team_id = fields.Many2one(
        comodel_name='football.team',
        string='Team',
        required=True,
        # domain="[('id_team', '=', id_team)]",
        # Relaciona por el campo id_team
    )
    # Relación con modelos de estadísticas
    all_stats_id = fields.Many2one(
        comodel_name='football.stats',
        string='All Stats'
    )
    # Campo relacionado
    played = fields.Integer(
        related='all_stats_id.played',
        string='Played',
        store=True
    )
    win = fields.Integer(
        related='all_stats_id.win',
        string='Wins',
        store=True
    )
    draw = fields.Integer(
        related='all_stats_id.draw',
        string='Draws',
        store=True
    )
    lose = fields.Integer(
        related='all_stats_id.lose',
        string='Losses',
        store=True
    )
    scored = fields.Integer(
        related='all_stats_id.scored',
        string='Goals Scored',
        store=True
    )
    conceded = fields.Integer(
        related='all_stats_id.conceded',
        string='Goals Conceded',
        store=True
    )

    home_stats_id = fields.Many2one(
        comodel_name='football.home.stats',
        string='Home Stats'
    )

    away_stats_id = fields.Many2one(
        comodel_name='football.away.stats',
        string='Away Stats'
    )

    # Campo para almacenar el id_team recibido desde la API
    id_team = fields.Integer(
        related='team_id.id_team',
        string='Team ID',
        store=True,
        readonly=True,
    )

    def _sync_standings(self):
        """Sync standings data from the API and update or
        create records in the database."""
        active_leagues = self.env['football.league'].search([
            ('follow', '=', True),
        ])

        base_url = os.getenv('API_FOOTBALL_URL')
        if not base_url:
            raise Exception(
                "API_FOOTBALL_URL is not defined. Please configure "
                "the environment variable."
            )
        url = base_url + '/standings'
        headers = {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

        _logger.info("\n\nStarting Sync\n\n")

        for league in active_leagues:
            params = {
                'league': league.id_league,
                'season': league.session_id.year
            }

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()
                # Raise HTTPError for bad responses

                data = response.json().get('response', [])
                self._process_standings(data, league)

            except requests.exceptions.HTTPError as http_err:
                _logger.error(f"\nHTTP error occurred: {http_err}\n")
            except requests.exceptions.ConnectionError as conn_err:
                _logger.error(f"\nConnection error occurred: {conn_err}\n")
            except requests.exceptions.Timeout as timeout_err:
                _logger.error(f"\nTimeout error occurred: {timeout_err}\n")
            except requests.exceptions.RequestException as req_err:
                _logger.error(f"\nRequest error occurred: {req_err}\n")
            except Exception as e:
                _logger.error(f"\nAn unexpected error occurred: {e}\n")

        _logger.info('\n\nSync Standings completed\n\n')

    def _process_standings(self, data, league):
        """Process and update or create standings records based on
        the API response."""
        for standings_data in data:
            league_data = standings_data.get('league', {})
            standings_list = league_data.get('standings', [[]])[0]

            for standing in standings_list:
                team_data = standing.get('team', {})
                all_stats_data = standing.get('all', {})
                home_stats_data = standing.get('home', {})
                away_stats_data = standing.get('away', {})

                team_id = team_data.get('id')
                team = self.env['football.team'].search(
                    [('id_team', '=', team_id)], limit=1
                )

                if not team:
                    _logger.warning(f"\nTeam: {team_id} not found.\n")
                    continue

                update_date = self._convert_date(standing.get('update'))

                existing_standing = self.env['football.standing'].search(
                    [
                        ('team_id', '=', team.id),
                        ('session_id', '=', league.session_id.id),
                        ('league_id', '=', league.id)
                    ],
                    limit=1
                )

                if existing_standing:
                    self._update_existing_standing(
                        existing_standing,
                        standing,
                        all_stats_data,
                        home_stats_data,
                        away_stats_data,
                        update_date
                    )
                else:
                    self._create_new_standing(
                        team,
                        league,
                        standing,
                        all_stats_data,
                        home_stats_data,
                        away_stats_data,
                        update_date
                    )

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

    def _update_existing_standing(
        self,
        existing_standing,
        standing,
        all_stats_data,
        home_stats_data,
        away_stats_data,
        update_date
    ):
        """Update an existing standing record with new data."""
        _logger.info(f"\nUpdating {existing_standing.team_id.name}\n")
        existing_standing.write({
            'rank': standing.get('rank'),
            'points': standing.get('points'),
            'goals_diff': standing.get('goalsDiff'),
            'status': standing.get('status'),
            'description': standing.get('description'),
            'update': update_date,
            'all_stats_id': self._update_stats(
                'football.stats',
                existing_standing.all_stats_id,
                all_stats_data
            ).id,
            'home_stats_id': self._update_stats(
                'football.home.stats',
                existing_standing.home_stats_id,
                home_stats_data
            ).id,
            'away_stats_id': self._update_stats(
                'football.away.stats',
                existing_standing.away_stats_id,
                away_stats_data
            ).id,
        })

    def _update_stats(self, model_name, stats_record, stats_data):
        """Update or create stats record in the specified model."""
        StatsModel = self.env[model_name]

        if stats_record:
            stats_record.write({
                'played': stats_data.get('played'),
                'win': stats_data.get('win'),
                'draw': stats_data.get('draw'),
                'lose': stats_data.get('lose'),
                'scored': stats_data.get('goals', {}).get('for'),
                'conceded': stats_data.get('goals', {}).get('against'),
            })
            return stats_record
        else:
            return StatsModel.create({
                'played': stats_data.get('played'),
                'win': stats_data.get('win'),
                'draw': stats_data.get('draw'),
                'lose': stats_data.get('lose'),
                'scored': stats_data.get('goals', {}).get('for'),
                'conceded': stats_data.get('goals', {}).get('against'),
            })

    def _create_new_standing(
        self,
        team,
        league,
        standing,
        all_stats_data,
        home_stats_data,
        away_stats_data,
        update_date
    ):
        """Create a new standing record."""
        all_stats = self._update_stats(
            'football.stats',
            None,
            all_stats_data
        )
        home_stats = self._update_stats(
            'football.home.stats',
            None,
            home_stats_data
        )
        away_stats = self._update_stats(
            'football.away.stats',
            None,
            away_stats_data
        )

        standings = self.env['football.standing'].create({
            'rank': standing.get('rank'),
            'points': standing.get('points'),
            'goals_diff': standing.get('goalsDiff'),
            'status': standing.get('status'),
            'description': standing.get('description'),
            'update': update_date,
            'team_id': team.id,
            'session_id': league.session_id.id,
            'league_id': league.id,
            'all_stats_id': all_stats.id,
            'home_stats_id': home_stats.id,
            'away_stats_id': away_stats.id,
        })

        _logger.info(f"Created standings for Team ID: {standings.id}")
