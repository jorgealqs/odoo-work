from odoo import models, fields


class CVSkill(models.Model):
    _name = "cv.skill"
    _description = "CV Skill"

    name = fields.Char(string="Skill", required=True)
    level = fields.Selection([
        ("principiante", "Principiante"),
        ("intermedio", "Intermedio"),
        ("experto", "Experto"),
    ], string="Level", default="principiante")
    cv_id = fields.Many2one("cv.manager", string="CV")
