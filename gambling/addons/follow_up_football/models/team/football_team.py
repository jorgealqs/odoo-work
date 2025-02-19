import logging
import requests  # type:ignore
import os
from odoo import models, fields
from requests.exceptions import RequestException  # type:ignore

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

    def _sync_teams(self, id_league=None):
        """Sync football teams for leagues marked as 'follow'."""
        active_leagues = self._get_active_leagues(id_league)
        for league in active_leagues:
            response = self._fetch_teams_from_api(league, id_league)
            if response and response.status_code == 200:
                teams_data = response.json().get('response', [])
                self._process_and_create_teams(teams_data, league)

    def _get_active_leagues(self, id_league=None):
        """Retrieve leagues marked as 'follow'."""
        query = [('follow', '=', True)]
        if id_league:
            query.append(('id_league', '=', id_league))
        return self.env['football.league'].search(query)

    def _fetch_teams_from_api(self, league, id_league=None):
        """
        Make API request to fetch teams for a
        specific league and session.
        """
        base_url = os.getenv('API_FOOTBALL_URL')
        if not base_url:
            raise Exception(
                "API_FOOTBALL_URL is not defined. Please configure "
                "the environment variable."
            )
        url = base_url + '/teams'
        headers = {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }
        params = {
            'season': league.session_id.year,
        }
        # Añadir el campo 'league' a params desde el inicio
        params['league'] = league.id_league
        if not id_league:
            params['country'] = league.country_id.name

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except RequestException as e:
            _logger.error(f"Error fetching teams for {league.name}: {e}")
            return None

    def _process_and_create_teams(self, teams_data, league):
        """Process and create teams based on API response."""
        for team_data in teams_data:
            team_info = team_data.get('team', {})
            # Crear el equipo solo si no existe
            existing_team = self.env['football.team'].search(
                [
                    ('id_team', '=', team_info.get('id')),
                    ('league_id', '=', league.id),
                    ('session_id', '=', league.session_id.id),
                ], limit=1
            )
            if not existing_team:
                venue = self._create_or_get_venue(team_data.get('venue'))
                if venue:
                    self._create_team_record(team_info, venue.id, league)
                    _logger.info(
                        f"Created team: {team_info.get('name')} "
                        f"in League: {league.name}"
                    )

    def _create_or_get_venue(self, venue_data):
        """Create or retrieve the venue based on venue data."""
        return self.env['football.venue'].create({
            'id_venue': venue_data.get('id'),
            'name': venue_data.get('name'),
            'address': venue_data.get('address', ''),
            'city': venue_data.get('city', ''),
            'capacity': venue_data.get('capacity', 0),
            'surface': venue_data.get('surface', ''),
            'image': venue_data.get('image', ''),
        })

    def _create_team_record(self, team_info, venue_id, league):
        """Create a new football team record."""
        self.env['football.team'].create({
            'name': team_info.get('name'),
            'id_team': team_info.get('id'),
            'code': team_info.get('code', ''),
            'founded': team_info.get('founded', 0),
            'national': team_info.get('national'),
            'logo': team_info.get('logo', ''),
            'venue_id': venue_id,
            'league_id': league.id,
            'session_id': league.session_id.id,
            'country_id': league.country_id.id,
        })
