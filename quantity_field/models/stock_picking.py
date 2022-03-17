from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    demand_qty_move = fields.Float(digits=(32,2),string='Demanda Movimiento',compute='_compute_demand_qty_move')
    done_qty_move = fields.Float(digits=(32,2),string='Hecho Movimiento',compute='_compute_done_qty_move')
    
    demand_qty_move_line = fields.Float(digits=(32,2),string='Demanda Movimiento Linea',compute='_compute_demand_qty_move_line')
    done_qty_move_line = fields.Float(digits=(32,2),string='Hecho Movimiento Linea',compute='_compute_done_qty_move_line')
    
    @api.depends('move_ids_without_package')
    def _compute_demand_qty_move(self):
        for picking in self:
            picking.demand_qty_move = sum(picking.move_ids_without_package.mapped('product_uom_qty'))
   
   
    @api.depends('move_ids_without_package')
    def _compute_done_qty_move(self):
        for picking in self:
            picking.done_qty_move = sum(picking.move_ids_without_package.mapped('quantity_done'))
            
            
    @api.depends('move_line_ids_without_package')
    def _compute_demand_qty_move_line(self):
        for picking in self:
            picking.demand_qty_move_line = sum(picking.move_line_ids_without_package.mapped('product_uom_qty'))
   
   
    @api.depends('move_line_ids_without_package')
    def _compute_done_qty_move_line(self):
        for picking in self:
            picking.done_qty_move_line = sum(picking.move_line_ids_without_package.mapped('quantity_done'))