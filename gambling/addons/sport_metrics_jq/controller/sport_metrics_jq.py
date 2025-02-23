from odoo import http
from odoo.http import request  # type: ignore
import logging

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
