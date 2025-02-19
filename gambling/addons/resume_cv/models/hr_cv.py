from odoo import models, fields


class HRCV(models.Model):
    _name = 'hr.cv'
    _description = 'Resume'

    name = fields.Char(string='Name', required=True, translate=True)
    job_title = fields.Char(string='Job title', translate=True)
    education = fields.Text(string='Education', translate=True)
    experience = fields.Text(string='Experience', translate=True)
    skills = fields.Text(string='Skills', translate=True)
    languages = fields.Text(string='Languages', translate=True)
    photo = fields.Binary(string='Photo')

    language = fields.Selection([
        ('es', 'Español'),
        ('en', 'Inglés')
    ], string='Language', default='es')
