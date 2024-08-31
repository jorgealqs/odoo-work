import os
import requests
import logging
from odoo import models, fields, api
from requests.exceptions import RequestException
from odoo.exceptions import ValidationError

# Configuring the logger to record relevant information in Odoo logs
_logger = logging.getLogger(__name__)


class FootballSession(models.Model):
    """
    Model representing a football season. Each record in this model
    is associated with a specific year and country, and is used to
    store the available seasons for each country.
    """

    _name = 'football.session'
    _description = 'Football Season'
    _order = "year desc, country_id asc"
    # Orders sessions by year in descending order,
    # then by country in ascending order.

    # Model fields
    year = fields.Char(string='Year', required=True)  # Year of the season.
    country_id = fields.Many2one(
        comodel_name='football.country',
        string='Country'
    )
    # Many2one relationship with the 'football.country' model,
    # indicating the country to which the season belongs.
    is_active = fields.Boolean(string='Active', default=False)
    # Indicates whether the season is active or not.

    @api.constrains('is_active')
    def _check_unique_active_session(self):
        """
        Validates that only one session can be active per country.
        """
        for record in self:
            if record.is_active:
                # Search for other active sessions in the same country
                active_sessions = self.search([
                    ('country_id', '=', record.country_id.id),
                    ('is_active', '=', True),
                    ('id', '!=', record.id)  # Exclude the current record
                ])
                if active_sessions:
                    raise ValidationError(
                        f"The country {record.country_id.name} "
                        f"already has an active "
                        f"session: ***{active_sessions.year}***"
                    )

    def _sync_sessions(self):
        """
        Method to synchronize football seasons from the Api-Football API.
        This method makes a GET request to the API, retrieves the
        list of available seasons, and saves them in the `football.session`
        model associated with each country.
        """
        url = 'https://v3.football.api-sports.io/leagues/seasons'
        # API URL to fetch seasons
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',  # API host
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
            # API key retrieved from environment variables
        }
        try:
            # Make the GET request to the API
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
            sessions = response.json().get('response', [])
            # Extract the list of seasons from the response
            _logger.info(f"\n\n{sessions}\n\n")  # Log the retrieved seasons

            countries = self.env['football.country'].search([])
            # Retrieve all countries

            # Iterate over each retrieved season
            for session in sessions:
                # Iterate over each country
                for country in countries:
                    # Check if a season already exists for the current
                    # year and country
                    existing_session = self.env['football.session'].search(
                        [
                            ('year', '=', session),
                            ('country_id', '=', country.id)
                        ], limit=1
                    )
                    if not existing_session:
                        # If not, create a new season
                        self.env['football.session'].create({
                            'year': session,
                            'country_id': country.id
                        })
                        _logger.info(
                            f"Session {session} created "
                            f"successfully for country {country.name}."
                        )  # Log that the season was created successfully
                    else:
                        # If it already exists, log that the season is
                        # already in the database
                        _logger.info(
                            f"Session {session} already "
                            f"exists for country {country.name}."
                        )

        except RequestException as e:
            # Handle any exceptions that occur during the API request
            raise Exception(f"Error fetching sessions from API: {str(e)}")
