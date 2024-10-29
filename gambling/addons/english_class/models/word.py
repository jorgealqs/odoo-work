from odoo import models, fields


class EnglishWord(models.Model):
    _name = 'english.word'
    _description = 'Word Catalog'

    name = fields.Char(string='Word', required=True)
    definition = fields.Html(string='Definition')
    pronunciation = fields.Char(string='Pronunciation')
    difficulty = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], string='Difficulty', default="")
    tag_ids = fields.Many2many(
        'english.word.tag',
        string='Tags'
    )
