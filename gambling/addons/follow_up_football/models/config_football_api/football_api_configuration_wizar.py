import logging
from odoo import models

_logger = logging.getLogger(__name__)


class FootballApiConfigurationWizard(models.TransientModel):
    _name = 'football.api.configuration.wizard'
    _description = 'Football Configuration Wizard'

    def action_sync_countries(self):
        model = self.env['football.country']
        model._sync_countries()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_seasons(self):
        model = self.env['football.session']
        model._sync_seasons()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_leagues(self):
        model = self.env['football.league']
        model._sync_leagues()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_teams(self):
        model = self.env['football.team']
        model._sync_teams()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_rounds(self):
        model = self.env['football.fixture.session.round']
        model._sync_rounds()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_standings(self):
        model = self.env['football.standing']
        model._sync_standings()
        return {'type': 'ir.actions.act_window_close'}

    def action_sync_fixtures(self):
        model = self.env['football.fixture']
        model._sync_fixtures()
        return {'type': 'ir.actions.act_window_close'}
