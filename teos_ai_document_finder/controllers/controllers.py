# -*- coding: utf-8 -*-
# from odoo import http


# class Teos(http.Controller):
#     @http.route('/teos/teos', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/teos/teos/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('teos.listing', {
#             'root': '/teos/teos',
#             'objects': http.request.env['teos.teos'].search([]),
#         })

#     @http.route('/teos/teos/objects/<model("teos.teos"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('teos.object', {
#             'object': obj
#         })

