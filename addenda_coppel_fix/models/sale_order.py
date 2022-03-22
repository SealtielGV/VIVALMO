from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order'
    
    
    partner_name = fields.Char(string='Cliente Nombre',related='partner_id.display_name')
    
    
