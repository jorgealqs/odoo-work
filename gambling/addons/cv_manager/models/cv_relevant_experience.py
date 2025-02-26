from odoo import models, fields


class CVRelevantExperience(models.Model):
    _name = 'cv.relevant.experience'
    _description = 'Relevant Experience'

    title = fields.Char(string="Title", required=True)
    job_position = fields.Char(string="Job Position", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    description = fields.Html(string="Description")
    cv_id = fields.Many2one('cv.manager', string="CV", ondelete='cascade')
