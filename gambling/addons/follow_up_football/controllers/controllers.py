from odoo.http import request, route, Controller  # noqa: F401


class ApiFootballController(Controller):
    @route(['/games'], type='http', auth='public')
    def api_football_games(self):
        return request.render(
            'follow_up_football.api_football_games',
            {
                'session_info': request.env[
                    'ir.http'
                ].get_frontend_session_info(),
            }
        )
