import logging
from odoo import models

_logger = logging.getLogger(__name__)


class FootballTeamWizard(models.TransientModel):
    _name = 'football.team.wizard'
    _description = 'Football Team Wizard'

    def action_sync_teams(self):
        model = self.env['football.team']
        model._sync_teams()
        return {'type': 'ir.actions.act_window_close'}
