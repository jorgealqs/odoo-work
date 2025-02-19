from odoo import models, fields


class CVManager(models.Model):
    _name = "cv.manager"
    _description = "CV Manager"

    name = fields.Char(string="Name", required=True)
    about_me = fields.Html(string="About Me")  # Campo con formato enriquecido
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    image_1920 = fields.Image(string="Photo")  # Imagen para la foto
    address_id = fields.Many2one("cv.address", string="Address")
    # Relación con dirección
    education = fields.Text(string="Education")
    experience = fields.Text(string="Experience")
    skill_ids = fields.One2many("cv.skill", "cv_id", string="Skills")
    # Relación con habilidades


class CVAddress(models.Model):
    _name = "cv.address"
    _description = "CV Address"

    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state = fields.Char(string="State")
    country = fields.Char(string="Country")


class CVSkill(models.Model):
    _name = "cv.skill"
    _description = "CV Skill"

    name = fields.Char(string="Skill", required=True)
    level = fields.Selection([
        ("beginner", "Beginner"),
        ("intermediate", "Intermediate"),
        ("expert", "Expert"),
    ], string="Level", default="beginner")
    cv_id = fields.Many2one("cv.manager", string="CV")
