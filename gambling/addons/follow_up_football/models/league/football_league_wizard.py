import logging
from odoo import models

_logger = logging.getLogger(__name__)


class FootballLeagueWizard(models.TransientModel):
    _name = 'football.league.wizard'
    _description = 'Football League Wizard'

    def action_sync_leagues(self):
        model = self.env['football.league']
        model._sync_leagues()
        return {'type': 'ir.actions.act_window_close'}
