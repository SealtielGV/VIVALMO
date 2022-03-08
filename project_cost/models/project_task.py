from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoProjectTask(models.Model):
    _inherit = 'project.task'
    
    
    x_studio_costo_de_materiales = fields.Float(digits=(32,2),string='Costo de materiales',compute='_compute_costo_de_materiales')
    x_studio_costo_de_operaciones = fields.Float(digits=(32,2),string='Costo de operaciones',compute='_compute_costo_de_operaciones')
    x_studio_costo_total = fields.Float(digits=(32,2),string='Costo total',compute='_compute_costo_total')
    
    stock_product_ids = fields.One2many('stock.valuation.layer','x_studio_pr_relacionada',string='Productos Consumidos')
    invoice_ids = fields.One2many('account.move','x_studio_orden_de_fabricacion_pr',string='Facturas de contratista')
    production_ids = fields.One2many('mrp.production','x_studio_pr',string='MO')
    scrap_ids = fields.One2many('stock.scrap','task_id',string='Desechos',domain=[('state','=','done')])
    
    price_unit_bom = fields.Float(digits=(32,2),string='Precio de venta Bom',compute='_get_price_unit_bom',
    help='Precio de venta de la lista de precio')
    delivery_quantities = fields.Float(digits=(32,2),string='Cantidades entregadas',compute='_compute_production_delivery',
    help='Cantidades producidas - Cantidades desechadas')
    estimated_utility = fields.Float(digits=(32,2),string='Utilidad estimada',compute='_compute_estimated_utility',
    help='Precio de venta Bom * Cantidades entregadas')
    utility = fields.Float(digits=(32,2),string='Utilidad MXN',compute='_compute_total_utility',
    help='Utilidad estimada - Costo total')
    porcentaje_utility  = fields.Float(digits=(32,2),string='Utilidad % MXN',compute='_compute_porcentaje_utility',
    help='Utilidad MXN/Utilidad estimada')
    
    
    @api.depends('production_ids','production_ids.bom_id')
    def _get_price_unit_bom(self):
        for task in self:
            task.price_unit_bom = sum(task.production_ids.bom_id.mapped('x_studio_utilidad_en_mxn_bom'))/len(task.production_ids) if task.production_ids else 0

    @api.depends('production_ids','production_ids.qty_produced','scrap_ids','scrap_ids.scrap_qty')
    def _compute_production_delivery(self):
        for task in self:
            task.delivery_quantites = sum(task.production_ids.mapped('qty_produced')) + sum(task.scrap_ids.mapped('scrap_qty'))
    
    @api.depends('price_unit_bom','delivery_quantities')
    def _compute_estimated_utility(self):
        for task in self:
            task.estimated_utility = task.price_unit_bom * task.delivery_quantities
            
    @api.depends('estimated_utility','x_studio_costo_total')
    def _compute_total_utility(self):
        for task in self:
            task.utility = task.estimated_utility - task.x_studio_costo_total
            
    @api.depends('utility','estimated_utility')
    def _compute_porcentaje_utility(self):
        for task in self:
            task.porcentaje_utility = task.utility/task.estimated_utility if task.estimated_utility > 0 else 0
    
    
    @api.depends('stock_product_ids')
    def _compute_costo_de_materiales(self):
        for task in self:
            task.x_studio_costo_de_materiales = sum(task.stock_product_ids.mapped('value'))*-1
    
    
    @api.depends('invoice_ids')
    def _compute_costo_de_operaciones(self):
        for task in self:
            task.x_studio_costo_de_operaciones = sum(task.invoice_ids.mapped('amount_total_signed'))*-1
        
    
    @api.depends('x_studio_costo_de_materiales','x_studio_costo_de_operaciones')
    def _compute_costo_total(self):
        for task in self:
            task.x_studio_costo_total = task.x_studio_costo_de_materiales+task.x_studio_costo_de_operaciones
        


    