from odoo import http
import logging

_logger = logging.getLogger(__name__)


class MatchController(http.Controller):

    @http.route('/match/details', type='json', auth="public")
    def match_details(self, **kw):
        fixture_id_table = kw.get('fixture_id_table')

        # Ejecutar la consulta SQL corregida
        http.request.env.cr.execute('''
            SELECT f.id AS fixture_id,
                f.date AS fixture_date,
                p.*,
                c.*
            FROM sport_metrics_jq_fixture f
            LEFT JOIN sport_metrics_jq_prediction p ON f.id = p.fixture_id
            LEFT JOIN sport_metrics_jq_prediction_comparison c ON
            f.id = c.fixture_id
            LEFT JOIN sport_metrics_jq_team t ON t.id = f.home_team_id
            WHERE f.id = %s
        ''', (fixture_id_table,))

        # Obtener el resultado de la consulta SQL
        prediction = http.request.env.cr.dictfetchall()

        # Imprimir el resultado de la consulta para depuración
        _logger.info("Query result: %s", prediction)

        return {
            'fixture': prediction,
        }

    @http.route('/match/all', type='json', auth="public")
    def get_all_fixtures(self, **kw):
        # Extract startOfDay and endOfDay from the request parameters
        start_of_day = kw.get('startOfDay')
        end_of_day = kw.get('endOfDay')
        _logger.info(f"\n\n errro {start_of_day}, {end_of_day} \n\n")

        # Ensure both start and end date are provided
        if not start_of_day or not end_of_day:
            return {"error": "Start and end dates are required"}

        query = '''SELECT f.id as id, f.fixture_id as fixture_id, f.date,
                home_team.id as home_team_id,
                home_team.name as home_team_name,
                away_team.id as away_team_id,
                away_team.name as away_team_name,
                home_standing.rank as home_team_rank,
                home_standing.points as home_team_points,
                away_standing.rank as away_team_rank,
                away_standing.points as away_team_points,
                league.name as league_name,
                country.name as country_name
            FROM sport_metrics_jq_fixture f
            JOIN sport_metrics_jq_team home_team
            ON f.home_team_id = home_team.id
            JOIN sport_metrics_jq_team away_team
            ON f.away_team_id = away_team.id
            LEFT JOIN sport_metrics_jq_standing home_standing
            ON home_standing.team_id = home_team.id
            AND home_standing.league_id = f.league_id
            LEFT JOIN sport_metrics_jq_standing away_standing
            ON away_standing.team_id = away_team.id
            AND away_standing.league_id = f.league_id
            JOIN sport_metrics_jq_league league
            ON f.league_id = league.id
            JOIN sport_metrics_jq_country country
            ON f.country_id = country.id
            WHERE f.date BETWEEN %s AND %s
            ORDER BY f.date
            '''

        http.request.env.cr.execute(query, (start_of_day, end_of_day))
        fixtures = http.request.env.cr.dictfetchall()

        # Return the result as JSON
        return {"fixtures": fixtures}
