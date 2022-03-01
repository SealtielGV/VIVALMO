from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoProjectTask(models.Model):
    _inherit = 'project.task'
    
    
    x_studio_costo_de_materiales = fields.Float(digits=(32,2),string='Costo de materiales',compute='_compute_costo_de_materiales')
    x_studio_costo_de_operaciones = fields.Float(digits=(32,2),string='Costo de operaciones',compute='_compute_costo_de_operaciones')
    x_studio_costo_total = fields.Float(digits=(32,2),string='Costo total',compute='_compute_costo_total')
    
    stock_product_ids = fields.One2many('stock.valuation.layer','x_studio_pr_relacionada',string='Productos Consumidos')
    invoice_ids = fields.One2many('account.move','x_studio_many2one_field_rHur1',string='Facturas de contratista')
    
    
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
            task.value = task.x_studio_costo_de_materiales+task.x_studio_costo_de_operaciones
        

    