from operator import is_
from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



class VivalmoProjectTask(models.Model):
    _inherit = 'project.task'
    
    
    x_studio_costo_de_materiales = fields.Float(digits=(32,2),string='Costo de materiales',compute='_compute_costo_de_materiales',
    help='Suma del costo de materailes utilizados en la PR')
    x_studio_costo_de_operaciones = fields.Float(digits=(32,2),string='Costo de operaciones',compute='_compute_costo_de_operaciones',
    help='Suma del total de facturas de contratista')
    x_studio_costo_total = fields.Float(digits=(32,2),string='Costo total',compute='_compute_costo_total',
    help='Costo total = Costo de materiales + Costo de operaciones')
    
    stock_product_ids = fields.One2many('stock.valuation.layer','x_studio_pr_relacionada',string='Productos Consumidos')
    invoice_ids = fields.One2many('account.move','x_studio_orden_de_fabricacion_pr',string='Facturas de contratista')
    production_ids = fields.One2many('mrp.production','x_studio_pr',string='MO')
    scrap_ids = fields.One2many('stock.scrap','task_id',string='Desechos',domain=[('state','=','done')])
    
    price_unit_bom = fields.Float(digits=(32,2),string='Precio de neto Bom',compute='get_price_unit_bom',
    help='Precio de venta de la lista de materiales')
    delivery_quantities = fields.Float(digits=(32,2),string='Cantidades entregadas',compute='_compute_production_delivery',
    help='Cantidades Recibidas = Cantidades producidas de MO - Cantidades desechadas')
    estimated_utility = fields.Float(digits=(32,2),string='Utilidad',compute='_compute_estimated_utility',
    help='Utilidad = Precio de venta Bom * Cantidades entregadas')
    utility = fields.Float(digits=(32,2),string='Utilidad estimada por PR en MXN',compute='_compute_total_utility',
    help='Utilidad estimada por PR en MXN = (Precio de neto Bom x Cantidades Recibidas) - Costo total')
    porcentaje_utility  = fields.Float(digits=(32,2),string='Utilidad % MXN',compute='_compute_porcentaje_utility',
    help='Utilidad % MXN = Utilidad estimada por PR en MXN/(Precio de neto Bom x Cantidades Recibidas)')
    
    planned_qty = fields.Float(string='Cantidad Planeada', readonly=True, compute='_compute_planned_qty', store=True)
    produced_qty = fields.Float(string='Cantidad Producida', readonly=True, compute='_compute_produced_qty', store=True)
    scrap_qty = fields.Float(string='Cantidad Desechos', readonly=True, compute='_compute_scrap_qty', store=True)
    is_end_stage = fields.Boolean(related='stage_id.is_closed', readonly=True, nocopy=True, default=False)
    #metodos compute para calcular los valores esperados por el cliente
    
    
    @api.depends('production_ids.product_qty', 'production_ids')
    def _compute_planned_qty(self):
        for record in self:
            qty = 0.00
            for production in record.production_ids:
                if production.state not in ['cancel', 'draft']:
                    qty += production.product_qty
            record.planned_qty = qty
    

    @api.depends('production_ids.x_studio_cantidad_producida', 'production_ids')
    def _compute_produced_qty(self):
        for record in self:
            qty = 0.00
            for production in record.production_ids:
                if production.state not in ['cancel', 'draft']:
                    qty += production.x_studio_cantidad_producida
            record.produced_qty = qty  
    

    @api.depends('production_ids', 'production_ids.scrap_ids', 'scrap_ids.scrap_qty')
    def _compute_scrap_qty(self):
        for record in self:
            qty = 0.00
            for production in record.production_ids:
                for i in production.scrap_ids:
                    qty += i.scrap_qty
            record.scrap_qty = qty


    @api.depends('production_ids','production_ids.bom_id')
    def get_price_unit_bom(self):
        for task in self:
            task.price_unit_bom = task.production_ids[0].bom_id.net_price if task.production_ids and task.production_ids.mapped('bom_id') else 0

    @api.depends('production_ids','production_ids.qty_produced','scrap_ids','scrap_ids.scrap_qty')
    def _compute_production_delivery(self):
        for task in self:
            task.delivery_quantities = sum(task.production_ids.mapped('qty_produced')) + sum(task.scrap_ids.mapped('scrap_qty'))
    
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
            price_total = task.price_unit_bom * task.delivery_quantities
            task.porcentaje_utility = task.utility/price_total if price_total > 0 else 0
    
    
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

    def write(self, vals):
        res = super(VivalmoProjectTask, self).write(vals)
        if 'stage_id' in vals.keys():
            is_end_stage = True if self.env['project.task.type'].search([('id', '=', vals['stage_id'])]).is_closed == True else False
            if is_end_stage:
                vals['date_end'] = lambda self: fields.Date.today()
        return res