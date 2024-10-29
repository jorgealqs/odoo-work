from odoo import models, fields


class Tag(models.Model):
    _name = 'english.word.tag'
    _description = 'Tag for Word'

    name = fields.Char(string='Tag', required=True)
    color = fields.Integer(string='Color')
