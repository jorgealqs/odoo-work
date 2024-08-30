import logging
from odoo import models

_logger = logging.getLogger(__name__)


class FootballCountryWizard(models.TransientModel):
    _name = 'football.country.wizard'
    _description = 'Football Country Wizard'

    def action_sync_countries(self):
        model = self.env['football.country']
        model.sync_countries()
        return {'type': 'ir.actions.act_window_close'}
