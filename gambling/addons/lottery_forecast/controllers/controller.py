from odoo import http
import logging

_logger = logging.getLogger(__name__)


class LotteryBalotoController(http.Controller):

    @http.route('/baloto116/details', type='json', auth="public")
    def baloto_r_1_16(self, **kw):
        frequency = http.request.env['lottery.baloto.number.frequency.1.16']
        results = frequency._frequency_1_16_panda("Baloto")
        return {
            'results': results,
        }
