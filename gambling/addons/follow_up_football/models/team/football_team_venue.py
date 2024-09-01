from odoo import models, fields


class FootballVenue(models.Model):
    _name = 'football.venue'
    _description = 'Football Venue'
    _order = "name ASC"

    id_venue = fields.Integer(string='Venue ID', required=True)
    name = fields.Char(string='Name', required=True)
    address = fields.Char(string='Address')
    city = fields.Char(string='City')
    capacity = fields.Integer(string='Capacity')
    surface = fields.Char(string='Surface')
    image = fields.Char(string='Image URL')
