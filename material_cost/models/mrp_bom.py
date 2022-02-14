from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBomCostTotal(models.Model):
    _inherit = 'mrp.bom'
    
    
    x_studio_total_de_materiales = fields.Float(digits=(32, 2),string='Total de materiales',compute='_compute_total_materiales_costo')
    x_studio_total_de_servicios = fields.Float(digits=(32, 2),string='Total de servicios',compute='_compute_total_servicios')
    x_studio_costos_indirectos = fields.Float(digits=(32, 2),string='Costos indirectos')
    x_studio_costo_total = fields.Float(digits=(32, 2),string='Costo total',compute='_compute_total_costo')
    x_studio_precio_de_venta_bom = fields.Float(digits=(32, 2),string='Precio de venta')
    x_studio_descuento_bom = fields.Float(digits=(32, 2),string='Descuento')
    x_studio_utilidad_en_mxn_bom = fields.Float(digits=(32, 2),string='Utilidad en MXN',compute='_compute_total_utilidad')
    x_studio_utilidad_porcentual_bom = fields.Float(digits=(32, 2),string='Utilidad en %',compute='_compute_porcentaje_utilidad')
    x_studio_se00001_servicio_de_corte = fields.Float(digits=(32, 2),string='SE00001 Servicio de corte')
    x_studio_se00002_servicio_de_bordado = fields.Float(digits=(32, 2),string='SE00002 Servicio de bordado')
    x_studio_se00003_servicio_de_costura = fields.Float(digits=(32, 2),string='SE00003 Servicio de costura')
    x_studio_se00004_servicio_de_lavado = fields.Float(digits=(32, 2),string='SE00004 Servicio de lavado')
    x_studio_se00005_servicio_de_terminado = fields.Float(digits=(32, 2),string='SE00005 Servicio de terminado')
    
    
    
    @api.depends('bom_line_ids')
    def _compute_total_materiales_costo(self):
        for bom in self:
            bom_total = 0.00
            product_tmpl_id = []
            for line in bom.bom_line_ids:
                if line.product_id.product_tmpl_id.id not in product_tmpl_id:
                    product_tmpl_id.append((line.product_id.product_tmpl_id.id))
                    bom_total += line.product_qty * line.x_studio_costo
            bom.x_studio_total_de_materiales = bom_total
            
            
    @api.depends('x_studio_se00001_servicio_de_corte','x_studio_se00002_servicio_de_bordado','x_studio_se00003_servicio_de_costura','x_studio_se00004_servicio_de_lavado','x_studio_se00005_servicio_de_terminado')
    def _compute_total_servicios(self):
        for bom in self:
            bom.x_studio_total_de_servicios = bom.x_studio_se00001_servicio_de_corte + bom.x_studio_se00002_servicio_de_bordado + bom.x_studio_se00003_servicio_de_costura + bom.x_studio_se00004_servicio_de_lavado + bom.x_studio_se00005_servicio_de_terminado 
                
                
    @api.depends('x_studio_total_de_materiales','x_studio_total_de_servicios','x_studio_costos_indirectos')
    def _compute_total_costo(self):
        for bom in self:
            bom.x_studio_costo_total = bom. x_studio_total_de_materiales + bom. x_studio_total_de_servicios + bom. x_studio_costos_indirectos
            
            
    @api.depends('x_studio_precio_de_venta_bom','x_studio_descuento_bom','x_studio_costo_total')
    def _compute_total_utilidad(self):
        for bom in self:
            
            amount = bom.x_studio_precio_de_venta_bom - ( bom.x_studio_precio_de_venta_bom * bom.x_studio_descuento_bom) - bom.x_studio_costo_total
            bom.x_studio_utilidad_en_mxn_bom = amount
            
            
    @api.depends('x_studio_utilidad_en_mxn_bom','x_studio_precio_de_venta_bom')
    def _compute_porcentaje_utilidad(self):
        for bom in self:
            bom.x_studio_utilidad_porcentual_bom = 1- (bom.x_studio_utilidad_en_mxn_bom / bom.x_studio_precio_de_venta_bom) if bom.x_studio_precio_de_venta_bom > 0.00 else 0.00
            
class CostoMrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    x_studio_costo = fields.Float(related='product_id.standard_price')
    amount_total = fields.Float('Total',compute='compute_value_total_amount')
    
    
    
    @api.depends('x_studio_costo')
    def compute_value_total_amount(self):
        for value in self:
            value.amount_total = value.product_qty * value.x_studio_costo