import logging
from odoo import models

_logger = logging.getLogger(__name__)


class FootballApiWizard(models.TransientModel):
    _name = 'football.api.wizard'
    _description = 'Football Api Wizard'

    def action_sync_sessions(self):
        model = self.env['football.fixture.session.round']
        model._sync_fixture_sessions()
        return {'type': 'ir.actions.act_window_close'}
