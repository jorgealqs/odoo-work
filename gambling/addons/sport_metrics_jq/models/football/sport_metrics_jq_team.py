import os
import logging
import requests
from requests.exceptions import RequestException
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class SportMetricsJQTeam(models.Model):
    _name = 'sport.metrics.jq.team'
    _description = 'SportMetricsJQ Team'
    _order = "name ASC"

    name = fields.Char(string='Name', required=True)
    id_team = fields.Integer(string='Team ID', required=True)
    code = fields.Char(string='Code')
    founded = fields.Integer(string='Founded Year')
    national = fields.Boolean(string='National')
    logo = fields.Char(string='Logo URL')
    # Campo computado que mostrará el nombre del equipo, estadio, e imágenes
    display_info = fields.Html(
        string='Team and Venue Info',
        compute='_compute_display_info'
    )

    # Adding the missing session_id field
    session_id = fields.Many2one(
        'sport.metrics.jq.session',
        string='Session',
        required=True
    )

    # Many2one relation to league
    league_id = fields.Many2one(
        'sport.metrics.jq.league',
        string='League',
        required=True
    )

    # Many2one relation to venue
    venue_id = fields.Many2one(
        'sport.metrics.jq.team.venue',
        string='Venue'
    )

    @api.depends('name', 'logo', 'venue_id.name', 'venue_id.image')
    def _compute_display_info(self):
        for record in self:
            team_image = record.logo or ''
            team_name = record.name or 'No Team Name'
            venue_name = record.venue_id.name or 'No Venue'
            venue_image = record.venue_id.image or ''

            record.display_info = f"""
                <div class='row'>
                    <!-- Columna para el equipo -->
                    <div class='col-md-6 text-center'>
                        <h5 class='mt-2' style='font-weight: bold;'>
                            {team_name}
                        </h5>
                        <img
                            src='{team_image}'
                            alt='Team Logo'
                            class='img-fluid rounded'
                            style='max-width: 45px; max-height: 45px;'
                        />
                    </div>
                    <!-- Columna para el estadio -->
                    <div class='col-md-6 text-center'>
                        <img
                            src='{venue_image}'
                            alt='Venue Image'
                            class='img-fluid rounded'
                            style='max-width: 45px; max-height: 45px;'
                        />
                        <h5 class='mt-2'>{venue_name}</h5>
                    </div>
                </div>
            """

    def _sync_teams(self, data=None):
        id_league = data.get('id_league')
        session = data.get('session')
        response = self._fetch_teams_from_api(id_league, session)
        if response and response.status_code == 200:
            teams_data = response.json().get('response', [])

            for team_data in teams_data:
                # Extract team and venue data
                team_info = team_data.get('team', {})
                venue_info = team_data.get('venue', {})

                if not team_info:
                    continue  # Skip if there's no team info

                # Create or update the venue
                venue = self._create_or_update_venue(venue_info)

                # Create or update the team
                self._create_or_update_team(
                    team_info, id_league, session, venue
                )

    def _fetch_teams_from_api(self, id_league=None, session=None):
        """
        Make API request to fetch teams for a
        specific league and session.
        """
        base_url = os.getenv('API_FOOTBALL_URL')
        url = base_url + '/teams'
        headers = {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }
        params = {
            'season': session,
        }
        # Añadir el campo 'league' a params desde el inicio
        params['league'] = id_league

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response
        except RequestException as e:
            _logger.error(f"Error fetching teams for {id_league}: {e}")
            return None

    def _create_or_update_venue(self, venue_data):
        """
        Create or update a venue based on the given data.
        Returns the venue record.
        """
        if not venue_data.get('id'):
            return None  # No venue data to process

        venue = self.env['sport.metrics.jq.team.venue'].search(
            [
                ('id_venue', '=', venue_data['id'])
            ], limit=1
        )

        if venue:
            # Update existing venue
            venue.write({
                'name': venue_data.get('name'),
                'address': venue_data.get('address'),
                'city': venue_data.get('city'),
                'capacity': venue_data.get('capacity'),
                'surface': venue_data.get('surface'),
                'image': venue_data.get('image'),
            })
        else:
            # Create a new venue
            venue = self.env['sport.metrics.jq.team.venue'].create({
                'id_venue': venue_data.get('id'),
                'name': venue_data.get('name'),
                'address': venue_data.get('address'),
                'city': venue_data.get('city'),
                'capacity': venue_data.get('capacity'),
                'surface': venue_data.get('surface'),
                'image': venue_data.get('image'),
            })

        return venue

    def _create_or_update_team(self, team_data, league, session_year, venue):
        """
        Create or update a team based on the given data, linking it to the
        league, session, and venue.
        """
        if not team_data.get('id'):
            return None  # No team data to process

        team = self.env['sport.metrics.jq.team'].search(
            [
                ('id_team', '=', team_data['id'])
            ], limit=1
        )

        # Fetch league and session IDs in bulk
        league = self.env[
            'sport.metrics.jq.league'
        ].search(
            [
                ('id_league', '=', league),
                ('session_id.year', '=', session_year),
            ], limit=1
        )
        session = self.env[
            'sport.metrics.jq.session'
        ].search([('year', '=', session_year)], limit=1)

        if not league:
            _logger.error(f"Country '{league}' not found in the system.")
            return
        if not session:
            _logger.error(f"Session '{session_year}' not found in the system.")
            return

        team_vals = {
            'name': team_data.get('name'),
            'code': team_data.get('code'),
            'founded': team_data.get('founded'),
            'national': team_data.get('national'),
            'logo': team_data.get('logo'),
            'league_id': league.id,  # Link to league
            'session_id': session.id,  # Link to session
            'venue_id': venue.id if venue else False,
        }

        if team:
            # Update existing team
            team.write(team_vals)
        else:
            # Create a new team
            self.env['sport.metrics.jq.team'].create({
                'id_team': team_data.get('id'),
                **team_vals
            })
