from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    
    prepact_cant = fields.Float(digits=(32, 2), string="Piezas por caja")
    pallet_quantity = fields.Float(digits=(32, 2), string="Total piezas")

    