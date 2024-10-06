import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQPredictionComparison(models.Model):
    _name = 'sport.metrics.jq.prediction.comparison'
    _description = 'SportMetricsJQ Prediction Teams Data Comparison'
    _rec_name = "fixture_id"

    # Relation with sport.metrics.jq.fixture'
    fixture_id = fields.Many2one(
        'sport.metrics.jq.fixture',
        string='Fixture',
        required=True,
    )
    comparison_form_home = fields.Char(string='Comparison form (Home)')
    comparison_form_away = fields.Char(string='Comparison form (Away)')
    comparison_att_home = fields.Char(string='Comparison att (Home)')
    comparison_att_away = fields.Char(string='Comparison att (Away)')
    comparison_def_home = fields.Char(string='Comparison def (Home)')
    comparison_def_away = fields.Char(string='Comparison def (Away)')
    comparison_poisson_distribution_home = fields.Char(
        string='Comparison poisson_distribution (Home)'
    )
    comparison_poisson_distribution_away = fields.Char(
        string='Comparison poisson_distribution (Away)'
    )
    comparison_goals_home = fields.Char(string='Comparison goals (Home)')
    comparison_goals_away = fields.Char(string='Comparison goals (Away)')
    comparison_total_home = fields.Char(string='Comparison total (Home)')
    comparison_total_away = fields.Char(string='Comparison total (Away)')

    def _create_or_update(self, **kw):
        comparison_data = kw.get("comparison", {})
        fixture_id_table = kw.get("fixture_id_table")
        existing_prediction_comparision = self.search(
            [
                ("fixture_id", "=", fixture_id_table)
            ], limit=1
        )
        prepared_comparison = self._prepare_comparison(
            comparison_data, fixture_id_table
        )
        # Actualizar o crear el registro correspondiente
        if existing_prediction_comparision:
            existing_prediction_comparision.write(prepared_comparison)
            _logger.info(
                "Updated prediction comparison for fixture ID: %s",
                fixture_id_table
            )
        else:
            self.create(prepared_comparison)
            _logger.info(
                "Created new prediction comparison for fixture ID: %s",
                fixture_id_table
            )

    def _prepare_comparison(self, comparison, fixture_id):
        if not comparison:
            _logger.error("Not comparison")
            return None
        form = comparison.get('form')
        att = comparison.get('att')
        defi = comparison.get('def')
        com_away = comparison.get(
            'poisson_distribution'
        )
        comparison_goals = comparison.get('goals')
        comparison_total = comparison.get('total')
        return {
            "fixture_id": fixture_id,
            "comparison_form_home": form.get('home'),
            "comparison_form_away": form.get('away'),
            "comparison_att_home": att.get('home'),
            "comparison_att_away": att.get('away'),
            "comparison_def_home": defi.get('home'),
            "comparison_def_away": defi.get('away'),
            "comparison_poisson_distribution_home": com_away.get('home'),
            "comparison_poisson_distribution_away": com_away.get('away'),
            "comparison_goals_home": comparison_goals.get('home'),
            "comparison_goals_away": comparison_goals.get('away'),
            "comparison_total_home": comparison_total.get('home'),
            "comparison_total_away": comparison_total.get('away'),
        }
