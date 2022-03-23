from odoo import models, fields, api, _
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    qty_total  = fields.Float(digits=(32,2),string="Canitdad",compute='_compute_qty_total')
    delivery_total  = fields.Float(digits=(32,2),string="Entregado",compute='_compute_delivery_total')
    invoicing_total  = fields.Float(digits=(32,2),string="Facturado",compute='_compute_invoicing_total')
    
    @api.depends('order_line')
    def _compute_qty_total(self):
        for purchase in self:
            purchase.qty_total = sum(purchase.order_line.mapped('product_qty'))
    
    
    @api.depends('order_line')
    def _compute_delivery_total(self):
        for purchase in self:
            purchase.delivery_total = sum(purchase.order_line.mapped('qty_received'))
    
    
    @api.depends('order_line')
    def _compute_invoicing_total(self):
        for purchase in self:
            purchase.invoicing_total = sum(purchase.order_line.mapped('qty_invoiced'))
            
