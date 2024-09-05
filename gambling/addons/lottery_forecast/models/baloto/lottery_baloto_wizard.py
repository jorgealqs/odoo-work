import logging
from odoo import models

_logger = logging.getLogger(__name__)


class LotteryBalotoWizard(models.TransientModel):
    _name = 'lottery.baloto.wizard'
    _description = 'Lottery Baloto Wizard'

    def action_sync_results(self):
        model = self.env['lottery.baloto']
        model._sync_results()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_results_miloto(self):
        model = self.env['lottery.baloto']
        model._sync_results_miloto()
        return {'type': 'ir.actions.act_window_close'}
