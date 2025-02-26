from odoo import models, fields


class CVAddress(models.Model):
    _name = "cv.address"
    _description = "Address"

    cv_id = fields.Many2one(
        "cv.manager",
        string="CV",
        required=True,
        ondelete="cascade",
        default=lambda self: self.env.context.get('default_cv_id')
    )
    street = fields.Char(string="Street")
    city = fields.Char(string="City")
    state = fields.Char(string="State")
    country = fields.Char(string="Country")
    is_primary = fields.Boolean(default=False)
