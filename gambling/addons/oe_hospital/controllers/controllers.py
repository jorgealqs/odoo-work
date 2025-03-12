# -*- coding: utf-8 -*-
# from odoo import http


# class OeHospital(http.Controller):
#     @http.route('/oe_hospital/oe_hospital', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/oe_hospital/oe_hospital/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('oe_hospital.listing', {
#             'root': '/oe_hospital/oe_hospital',
#             'objects': http.request.env['oe_hospital.oe_hospital'].search([]),
#         })

#     @http.route('/oe_hospital/oe_hospital/objects/<model("oe_hospital.oe_hospital"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('oe_hospital.object', {
#             'object': obj
#         })

