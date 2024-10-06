import os
import logging
import requests
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQPrediction(models.Model):
    _name = 'sport.metrics.jq.prediction'
    _description = 'SportMetricsJQ Prediction for a match'
    _rec_name = "fixture_id"

    winner = fields.Many2one(
        'sport.team',
        string='Winner',
        help='Predicted winning team'
    )
    comment = fields.Char(string="Comment", help='Prediction of prediction')
    win_or_draw = fields.Boolean(
        string='Win or Draw',
        help='True if win or draw is predicted'
    )
    under_over = fields.Char(string='Under/Over Goals')
    goals_home = fields.Float(
        string='Goals Prediction',
        help='Prediction of goals home'
    )
    goals_away = fields.Float(
        string='Goals Prediction',
        help='Prediction of goals away'
    )
    advice = fields.Text(string='Advice', help='Prediction advice')
    percent_home = fields.Char(
        string='Home Win Probability',
        help='Probability for home team win'
    )
    percent_draw = fields.Char(
        string='Draw Probability',
        help='Probability for draw'
    )
    percent_away = fields.Char(
        string='Away Win Probability',
        help='Probability for away team win'
    )

    # Relation with sport.metrics.jq.fixture'.teams
    fixture_id = fields.Many2one(
        comodel_name='sport.metrics.jq.fixture',
        string='Fixture',
        required=True,
    )

    def _make_api_request(self, headers, params):
        base_url = os.getenv('API_FOOTBALL_URL')
        url = f"{base_url}/predictions"
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            _logger.error(f"Error fetching data from API: {e}")
            return None

    def _get_api_params(self, fixture_id):
        """
        Build the API parameters for the league.
        """
        return {
            'fixture': fixture_id,
        }

    def _sync_predictions(self, **kw):
        if not kw.get('fixture_id'):
            _logger.error('Fixture ID is missing')
            return
        data = {
            'headers': self._get_api_headers(),
            'fixture_id': kw.get('fixture_id'),
            'fixture_id_table': kw.get('fixture_id_table'),
            'league_id': kw.get('league_id'),
            'session_id': kw.get('session_id'),
        }
        self._sync_predictions_process(**data)

    def _get_api_headers(self):
        """
        Retrieve API headers for the Football API.
        """
        return {
            'x-rapidapi-host': os.getenv('API_FOOTBALL_URL_V3'),
            'x-rapidapi-key': os.getenv('API_FOOTBALL_KEY')
        }

    def _sync_predictions_process(self, **kw):
        params = self._get_api_params(kw.get('fixture_id'))
        response_data = self._make_api_request(kw.get('headers'), params)
        if response_data:
            predictions = response_data.get('response', [])
            if not predictions:
                _logger.warning(
                    "No predictions found for fixture "
                    f"{kw.get('fixture_id')}"
                    )
                return
            for prediction in predictions:
                data_info = {
                    "predictions": prediction.get("predictions"),
                    "teams": prediction.get("teams"),
                    "comparison": prediction.get("comparison"),
                    "fixture_id": kw.get('fixture_id_table'),
                    'league_id': kw.get('league_id'),
                    'session_id': kw.get('session_id'),
                }
                self._process_prediction(**data_info)

    def _process_prediction(self, **kw):
        model_comparison = self.env['sport.metrics.jq.prediction.comparison']
        model_comparison._create_or_update(
            **{
                'comparison': kw.get("comparison", None),
                'fixture_id_table': kw.get("fixture_id", None)

            }
        )
        model_teams = self.env['sport.metrics.jq.prediction.teams']
        model_teams._create_or_update(
            **{
                'teams': kw.get("teams"),
                'fixture_id_table': kw.get("fixture_id"),
                'league_id': kw.get('league_id'),
                'session_id': kw.get('session_id'),
            }
        )
        existing_prediction = self.search(
            [
                ('fixture_id', '=', kw.get("fixture_id"))
            ], limit=1
        )

        if existing_prediction:
            info = {
                'predictions': kw.get("predictions"),
                "fixture_id": kw.get("fixture_id"),
            }
            _logger.info(f"\n\n {info} \n\n")
            predictions = self._prepare_predictions(**info)
            existing_prediction.write(predictions)
        else:

            info = {
                'predictions': kw.get("predictions"),
                "fixture_id": kw.get("fixture_id"),
            }
            predictions = self._prepare_predictions(**info)
            self.env['sport.metrics.jq.prediction'].create(predictions)

    def _prepare_predictions(self, **kw):
        if not kw.get('predictions'):
            _logger.error("Not predictions")
            return None
        predictions = kw.get('predictions')
        return {
            "winner": predictions.get('winner').get('id'),
            "comment": predictions.get('winner').get('comment'),
            "win_or_draw": predictions.get('win_or_draw'),
            "under_over": predictions.get('under_over'),
            "goals_home": predictions.get('goals').get('home'),
            "goals_away": predictions.get('goals').get('away'),
            "advice": predictions.get('advice'),
            "percent_home": predictions.get('percent').get('home'),
            "percent_draw": predictions.get('percent').get('draw'),
            "percent_away": predictions.get('percent').get('away'),
            "fixture_id": kw.get('fixture_id'),
        }
