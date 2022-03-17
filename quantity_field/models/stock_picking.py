from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    demand_qty = fields.Float(digits=(32,2),string='Demanda',compute='_compute_demand_qty')
    done_qty = fields.Float(digits=(32,2),string='Hecho',compute='_compute_done_qty')
    
    @api.depends('move_ids_without_package')
    def _compute_demand_qty(self):
        for picking in self:
            picking.demand_qty = sum(picking.move_ids_without_package.mapped('product_uom_qty'))
   
   
    @api.depends('move_ids_without_package')
    def _compute_done_qty(self):
        for picking in self:
            picking.done_qty = sum(picking.move_ids_without_package.mapped('quantity_done'))