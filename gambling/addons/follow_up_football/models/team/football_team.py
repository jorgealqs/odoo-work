import logging
import requests
import os
from odoo import models, fields
from requests.exceptions import RequestException

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

    def _sync_teams(self):
        """Sync football teams for leagues marked as 'follow'."""
        _logger.info('Sync Teams started.')

        active_leagues = self._get_active_leagues()

        for league in active_leagues:
            # if self._teams_exist(league):
            #     _logger.info(
            #         f"Teams already exist for League: {league.name} "
            #         f"({league.country_id.name}, {league.session_id.year}). "
            #         f"Skipping API request."
            #     )
            #     continue

            response = self._fetch_teams_from_api(league)

            if response and response.status_code == 200:
                teams_data = response.json().get('response', [])
                self._process_and_create_teams(teams_data, league)
            else:
                _logger.error(
                    f"Failed to fetch teams for League: {league.name} "
                    f"({league.country_id.name}, {league.session_id.year}). "
                    "Status Code: "
                    f"{response.status_code if response else 'No Response'}"
                )

        _logger.info('Sync Teams completed.')

    def _get_active_leagues(self):
        """Retrieve leagues marked as 'follow'."""
        return self.env['football.league'].search([('follow', '=', True)])

    def _teams_exist(self, league):
        """Check if teams already exist for a league, session, and country."""
        return self.env['football.team'].search_count([
            ('league_id', '=', league.id),
            ('session_id', '=', league.session_id.id),
            ('country_id', '=', league.country_id.id)
        ]) > 0

    def _fetch_teams_from_api(self, league):
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
            'country': league.country_id.name,
            'league': league.id_league,
            'season': league.session_id.year,
        }

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
            venue = self._create_or_get_venue(team_data.get('venue'))

            if venue:
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
                    self._create_team_record(team_info, venue.id, league)
                    _logger.info(
                        f"Created team: {team_info.get('name')} "
                        f"in League: {league.name}"
                    )

    def _create_or_get_venue(self, venue_data):
        """Create or retrieve the venue based on venue data."""
        if not venue_data or not venue_data.get('name'):
            _logger.warning(f"Venue name missing for venue data: {venue_data}")
            return None

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
