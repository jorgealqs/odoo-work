import logging
from odoo import models

_logger = logging.getLogger(__name__)


class FootballStandingWizard(models.TransientModel):
    _name = 'football.standing.wizard'
    _description = 'Football Standing Wizard'

    def action_sync_standings(self):
        model = self.env['football.standing']
        model._sync_standings()
        return {'type': 'ir.actions.act_window_close'}
