from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    qty_total  = fields.Float(digits=(32,2),string="Canitdad",compute='_compute_qty_total')
    delivery_total  = fields.Float(digits=(32,2),string="Entregado",compute='_compute_delivery_total')
    invoicing_total  = fields.Float(digits=(32,2),string="Facturado",compute='_compute_invoicing_total')
    
    @api.depends('order_line')
    def _compute_qty_total(self):
        for sale in self:
            sale.qty_total = sum(sale.order_line.mapped('product_uom_qty'))
    
    
    @api.depends('order_line')
    def _compute_delivery_total(self):
        for sale in self:
            sale.delivery_total = sum(sale.order_line.mapped('qty_delivered'))
    
    
    @api.depends('order_line')
    def _compute_invoicing_total(self):
        for sale in self:
            sale.invoicing_total = sum(sale.order_line.mapped('qty_invoiced'))