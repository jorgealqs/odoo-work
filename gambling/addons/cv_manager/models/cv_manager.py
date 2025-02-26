from odoo import models, fields


class CVManager(models.Model):
    _name = "cv.manager"
    _description = "CV Manager"

    name = fields.Char(string="Name", required=True)
    about_me = fields.Html(string="About Me")  # Campo con formato enriquecido
    email = fields.Char(string="Email")
    phone = fields.Char(string="Phone")
    image_1920 = fields.Binary(string="Photo")  # Imagen para la foto
    # Relación con la dirección del CV
    address_ids = fields.One2many(
        "cv.address",
        "cv_id",
        string="Address"
    )
    # Relación con dirección
    education_ids = fields.One2many(
        "cv.education",
        "cv_id",
        string="Education"
    )
    # Relación con habilidades
    skill_ids = fields.One2many("cv.skill", "cv_id", string="Skills")
    # Relación con experiencia
    relevant_experience_ids = fields.One2many(
        "cv.relevant.experience",
        "cv_id",
        string="Relevant Experience"
    )
    # Relación con redes sociales
    social_media_ids = fields.One2many(
        "cv.social.media",
        "cv_id",
        string="Redes Sociales"
    )
