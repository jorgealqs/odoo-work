from odoo import http    # type: ignore
from odoo.http import request  # type: ignore
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)


class SportMetricsJQ(http.Controller):

    @http.route(
        '/sport/metrics/sync_predictions',
        type='json',
        auth='user',
        methods=['POST']
    )
    def sync_predictions(self, **kwargs):
        """Servicio web para llamar a _sync_predictions desde JS"""
        data = kwargs.get('params')
        _logger.info(f"\n\n\n {data} \n\n")
        model_prediction = request.env['sport.metrics.jq.prediction']
        model_prediction._sync_predictions(**data)
        return {'status': 'success', 'result': model_prediction}

    @http.route(
        '/sport/metrics/info',
        type='json',
        auth='user',
        methods=['POST']
    )
    def show_metrics_info(self, **kw):
        # Obtener la fecha actual
        today = datetime.now().strftime('%Y-%m-%d')  # Formato: YYYY-MM-DD

        # Definir los límites de tiempo
        start_of_day = f"{today} 00:00:00"
        end_of_day = f"{today} 23:59:59"

        query = '''SELECT
                f.id as id, f.fixture_id as fixture_id,
                f.date, f.session_id,
                home_team.id as home_team_id,
                home_team.name as home_team_name,
                away_team.id as away_team_id,
                away_team.name as away_team_name,
                home_standing.rank as home_team_rank,
                home_standing.points as home_team_points,
                away_standing.rank as away_team_rank,
                away_standing.points as away_team_points,
                league.name as league_name,
                league.id as id_league,
                country.name as country_name,
                p.*,
                c.*
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
            LEFT JOIN sport_metrics_jq_prediction p ON f.id = p.fixture_id
            LEFT JOIN sport_metrics_jq_prediction_comparison c ON
            f.id = c.fixture_id
            LEFT JOIN sport_metrics_jq_team t ON t.id = f.home_team_id
            WHERE f.date BETWEEN %s AND %s
            AND league.follow = TRUE
            ORDER BY p.percent_home DESC, p.percent_away DESC
            '''

        http.request.env.cr.execute(query, (start_of_day, end_of_day))
        fixtures = http.request.env.cr.dictfetchall()
        return {
            'fixtures': fixtures,
        }
