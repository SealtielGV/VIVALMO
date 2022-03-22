from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = 'ProductTemplate'
    
    
    x_code = fields.Char(string='Código Coppel',compute="_compute_x_code",inverse="_set_x_code", store=True)
    x_size = fields.Char(string='Talla Coppel',compute="_compute_x_size",inverse="_set_x_size", store=True)
    x_model = fields.Char(string='Modelo Coppel',compute="_compute_x_model",inverse="_set_x_model", store=True)
 
    