# from odoo import http


# class FestivalBonus(http.Controller):
#     @http.route('/festival_bonus/festival_bonus', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/festival_bonus/festival_bonus/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('festival_bonus.listing', {
#             'root': '/festival_bonus/festival_bonus',
#             'objects': http.request.env['festival_bonus.festival_bonus'].search([]),
#         })

#     @http.route('/festival_bonus/festival_bonus/objects/<model("festival_bonus.festival_bonus"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('festival_bonus.object', {
#             'object': obj
#         })

