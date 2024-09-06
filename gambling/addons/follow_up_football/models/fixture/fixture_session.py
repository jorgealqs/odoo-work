import logging
import requests
import os
# import time
from odoo import models, fields, api  # noqa: F401

_logger = logging.getLogger(__name__)


class FootballFixtureSessionRound(models.Model):
    _name = 'football.fixture.session.round'
    _description = 'Football Fixture Session'
    _order = 'name ASC'

    name = fields.Char(string='Round Name', required=True)
    league_id = fields.Many2one(
        comodel_name='football.league',
        string='League',
        required=True
    )

    def _sync_fixture_sessions(self):
        """Sync fixture sessions (rounds) for leagues that are followed."""
        # Obtener todas las ligas que están marcadas para ser seguidas
        football_leagues = self.env['football.league'].search(
            [
                ('follow', '=', True),
                # ('country_id.name', 'in', ['Spain', 'Peru', 'Italy'])
            ]
        )

        url = "https://v3.football.api-sports.io/fixtures/rounds"
        headers = {
            'x-rapidapi-host': 'v3.football.api-sports.io',
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

        if football_leagues:
            for league in football_leagues:
                id_league = league.id_league
                session_year = league.session_id.year

                # Definir los parámetros para la petición
                params = {
                    'league': id_league,
                    'season': session_year
                }

                try:
                    # Hacer la petición GET a la API
                    response = requests.get(
                        url,
                        headers=headers,
                        params=params
                    )
                    response.raise_for_status()
                    # Verificar si hay errores HTTP
                    rounds_data = response.json().get('response', [])

                    _logger.info(
                        f"\n League {id_league}, \nSeason {session_year} "
                        f"\nRound {len(rounds_data)} "
                        f"\nName: {league.name}"
                        f"\nCountry: {league.country_id.name}"
                    )

                    # Procesar los datos obtenidos
                    for round_name in rounds_data:
                        # Verificar si ya existe un round con el mismo
                        # nombre y liga
                        existing_round = self.env[
                            'football.fixture.session.round'
                        ].search([
                            ('name', '=', round_name),
                            ('league_id', '=', league.id)
                        ], limit=1)
                        if not existing_round:
                            self.env['football.fixture.session.round'].create({
                                'name': round_name,
                                'league_id': league.id,
                            })
                            _logger.info(
                                f"Created round {round_name} for "
                                f"league {league.name}"
                            )
                        # Pausar para evitar sobrepasar el
                        # límite de solicitudes
                        # time.sleep(5)
                        # Pausa de 5 segundos entre cada solicitud

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
