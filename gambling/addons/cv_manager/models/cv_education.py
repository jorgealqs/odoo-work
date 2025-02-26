from odoo import models, fields


class CVEducation(models.Model):
    _name = "cv.education"
    _description = "Education"

    cv_id = fields.Many2one(
        "cv.manager",
        string="CV",
        required=True,
        ondelete="cascade"
    )
    title = fields.Char(string="Degree/Title", required=True)
    institution = fields.Char(string="Institution", required=True)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    description = fields.Text(string="Additional Information")
