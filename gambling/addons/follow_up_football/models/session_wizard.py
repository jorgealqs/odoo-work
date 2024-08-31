import logging
from odoo import models

_logger = logging.getLogger(__name__)


class FootballSessionWizard(models.TransientModel):
    _name = 'football.session.wizard'
    _description = 'Football Sesssion Wizard'

    def action_sync_sessions(self):
        model = self.env['football.session']
        model._sync_sessions()
        return {'type': 'ir.actions.act_window_close'}
