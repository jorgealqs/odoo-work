from odoo import api, models, fields


ICON_URLS = {
    'linkedin': 'https://cdn-icons-png.flaticon.com/512/174/174857.png',
    'github': 'https://cdn-icons-png.flaticon.com/512/25/25231.png',
    'twitter': 'https://cdn-icons-png.flaticon.com/512/733/733579.png',
    'facebook': 'https://cdn-icons-png.flaticon.com/512/733/733547.png',
    'instagram': 'https://cdn-icons-png.flaticon.com/512/2111/2111463.png',
    'youtube': 'https://cdn-icons-png.flaticon.com/512/1384/1384060.png',
    'tiktok': 'https://cdn-icons-png.flaticon.com/512/3046/3046125.png',
    'stackoverflow': 'https://cdn-icons-png.flaticon.com/512/2111/2111628.png',
    'behance': 'https://cdn-icons-png.flaticon.com/512/2111/2111501.png',
    'dribbble': 'https://cdn-icons-png.flaticon.com/512/2111/2111520.png',
    'medium': 'https://cdn-icons-png.flaticon.com/512/2111/2111543.png',
    'reddit': 'https://cdn-icons-png.flaticon.com/512/2111/2111589.png',
    'whatsapp': 'https://cdn-icons-png.flaticon.com/512/733/733585.png',
    'telegram': 'https://cdn-icons-png.flaticon.com/512/2111/2111646.png',
    'snapchat': 'https://cdn-icons-png.flaticon.com/512/2111/2111670.png',
}


class CVSocialMedia(models.Model):
    _name = "cv.social.media"
    _description = "Redes Sociales"

    name = fields.Selection([
        ('', 'Seleccion una red social'),
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('twitter', 'Twitter (X)'),
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('stackoverflow', 'Stack Overflow'),
        ('behance', 'Behance'),
        ('dribbble', 'Dribbble'),
        ('medium', 'Medium'),
        ('reddit', 'Reddit'),
        ('whatsapp', 'WhatsApp'),
        ('telegram', 'Telegram'),
        ('snapchat', 'Snapchat'),
    ], default="", required=True)
    url = fields.Char(string="URL", required=True)
    cv_id = fields.Many2one(
        "cv.manager",
        ondelete="cascade",
        default=lambda self: self.env.context.get('default_cv_id')
    )
    icon_url = fields.Char(string="Icono URL", compute="_compute_icon_url")

    @api.depends('name')
    def _compute_icon_url(self):
        for record in self:
            record.icon_url = ICON_URLS.get(record.name, '')
