import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)


class SportMetricsJQPredictionTeams(models.Model):
    _name = 'sport.metrics.jq.prediction.teams'
    _description = 'SportMetricsJQ Prediction Teams Data'
    _rec_name = "fixture_id"

    # General team information
    team_id = fields.Many2one(
        'sport.metrics.jq.team',
        string='Team',
        required=True
    )
    fixture_id = fields.Many2one(
        'sport.metrics.jq.fixture',
        string='Fixture',
        required=True
    )

    # Last 5 match stats
    form = fields.Char(string='Form')
    attack = fields.Char(string='Attack %')
    defense = fields.Char(string='Defense %')
    goals_for_total = fields.Integer(string='Goals For (Total)')
    goals_for_avg = fields.Float(string='Goals For (Average)')
    goals_against_total = fields.Integer(string='Goals Against (Total)')
    goals_against_avg = fields.Float(string='Goals Against (Average)')

    # League fixtures stats
    played_home = fields.Integer(string='Matches Played (Home)')
    played_away = fields.Integer(string='Matches Played (Away)')
    played_total = fields.Integer(string='Matches Played (Total)')

    wins_home = fields.Integer(string='Wins (Home)')
    wins_away = fields.Integer(string='Wins (Away)')
    wins_total = fields.Integer(string='Wins (Total)')

    draws_home = fields.Integer(string='Draws (Home)')
    draws_away = fields.Integer(string='Draws (Away)')
    draws_total = fields.Integer(string='Draws (Total)')

    loses_home = fields.Integer(string='Losses (Home)')
    loses_away = fields.Integer(string='Losses (Away)')
    loses_total = fields.Integer(string='Losses (Total)')

    # Goals stats in the league
    league_goals_for_total_home = fields.Integer(string='Goals For (Home)')
    league_goals_for_total_away = fields.Integer(string='Goals For (Away)')
    league_goals_for_total_total = fields.Integer(string='Goals For (Total)')

    league_goals_for_avg_home = fields.Integer(string='Goals For (Home)')
    league_goals_for_avg_away = fields.Integer(string='Goals For (Away)')
    league_goals_for_avg_total = fields.Integer(string='Goals For (Total)')

    league_goals_against_total_home = fields.Integer(
        string='Goals Against (Home)'
    )
    league_goals_against_total_away = fields.Integer(
        string='Goals Against (Away)'
    )
    league_goals_against_total_total = fields.Integer(
        string='Goals Against (Total)'
    )

    league_goals_avg_total_home = fields.Integer(string='Goals Against (Home)')
    league_goals_avg_total_away = fields.Integer(string='Goals Against (Away)')
    league_goals_avg_total_total = fields.Integer(
        string='Goals Against (Total)'
    )

    # Biggest
    biggest_streak_wins = fields.Integer(string='Biggest streak (Wins)')
    biggest_streak_draws = fields.Integer(string='Biggest streak (Draw)')
    biggest_streak_loses = fields.Integer(string='Biggest streak (Loses)')

    biggest_wins_home = fields.Char(string='Biggest streak (Home)')
    biggest_wins_away = fields.Char(string='Biggest streak (Away)')

    biggest_loses_home = fields.Char(string='Biggest streak (Home)')
    biggest_loses_away = fields.Char(string='Biggest streak (Away)')

    biggest_goals_for_home = fields.Integer(string='Biggest Goals For (Home)')
    biggest_goals_for_away = fields.Integer(string='Biggest Goals For (Away)')

    biggest_goals_against_home = fields.Integer(string='Biggest streak (Home)')
    biggest_goals_against_away = fields.Integer(string='Biggest streak (Away)')

    # Clean sheets and failed to score
    clean_sheet_home = fields.Integer(string='Clean Sheets (Home)')
    clean_sheet_away = fields.Integer(string='Clean Sheets (Away)')
    clean_sheet_total = fields.Integer(string='Clean Sheets (Total)')

    failed_to_score_home = fields.Integer(string='Failed to Score (Home)')
    failed_to_score_away = fields.Integer(string='Failed to Score (Away)')
    failed_to_score_total = fields.Integer(string='Failed to Score (Total)')

    def _create_or_update(self, **kw):
        teams = kw.get("teams")
        fixture_id_table = kw.get("fixture_id_table")

        home_team_api_id = teams.get('home').get('id')
        away_team_api_id = teams.get('away').get('id')

        if (
            not fixture_id_table
            or not home_team_api_id
            or not away_team_api_id
        ):
            _logger.error("Missing fixture ID or team IDs.")
            return

        home_team_id = self._get_id_team(
            home_team_api_id,
            kw.get("league_id"),
            kw.get("session_id")
        )
        away_team_id = self._get_id_team(
            away_team_api_id,
            kw.get("league_id"),
            kw.get("session_id")
        )

        # Preparar y actualizar la comparación para el equipo local
        self._update_or_create_prediction_team(
            home_team_id,
            fixture_id_table,
            teams.get('home')
        )

        # Preparar y actualizar la comparación para el equipo visitante
        self._update_or_create_prediction_team(
            away_team_id,
            fixture_id_table,
            teams.get('away')
        )

    def _get_id_team(self, team_api_id, league_id, session_id):
        team_record = self.env['sport.metrics.jq.team'].search(
            [
                ("id_team", "=", team_api_id),
                ("session_id.id", "=", session_id),
                ("league_id.id", "=", league_id),
            ], limit=1
        )
        # Retorna el ID del equipo o False si no se encontró
        return team_record.id if team_record else False

    def _update_or_create_prediction_team(
            self,
            team_id,
            fixture_id,
            team_data
    ):
        existing_team_prediction = self.search([
            ("team_id", "=", team_id),
            ("fixture_id", "=", fixture_id),
        ], limit=1)

        prepared_comparison = self._prepare_team(
            team_data,
            fixture_id,
            team_id
        )

        _logger.info(f"\n\nPprepared_comparison {prepared_comparison} \n\n")

        if existing_team_prediction:
            existing_team_prediction.write(prepared_comparison)
            _logger.info("Updated team for team ID: %s", team_id)
        else:
            self.create(prepared_comparison)
            _logger.info("Created new team for team ID: %s", team_id)

    def _prepare_team(self, team, fixture_id, team_id):
        if not team:
            _logger.error("Not team")
            return None
        last_5 = team.get('last_5')
        last_5_goals_for = last_5.get('goals').get('for')
        last_5_goals_againts = last_5.get('goals').get('against')
        return {
            'team_id': team_id,
            "fixture_id": fixture_id,
            "form": last_5.get('form'),
            "attack": last_5.get('att'),
            "defense": last_5.get('def'),
            "goals_for_total": last_5_goals_for.get('total'),
            "goals_for_avg": last_5_goals_for.get('average'),
            "goals_against_total": last_5_goals_againts.get('total'),
            "goals_against_avg": last_5_goals_againts.get('average')
        }
