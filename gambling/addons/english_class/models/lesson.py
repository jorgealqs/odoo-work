from odoo import models, fields


class EnglishLesson(models.Model):
    _name = 'english.lesson'
    _description = 'Lesson'

    name = fields.Char(string='Title', required=True)
    description = fields.Text(string='Description')
    content = fields.Html(string='Content')
    audio = fields.Binary(string='Audio')
    video = fields.Binary(string='Video')
    exercise_ids = fields.One2many(
        'english.exercise',
        'lesson_id',
        string='Exercises'
    )
