from odoo import models, fields


class EnglishExercise(models.Model):
    _name = 'english.exercise'
    _description = 'Exercise'

    question = fields.Text(string='Question', required=True)
    correct_answer = fields.Char(string='Correct Answer', required=True)
    lesson_id = fields.Many2one('english.lesson', string='Lesson')
