from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBomCostTotal(models.Model):
    _inherit = 'mrp.bom'
    
    
    x_studio_total_de_materiales = fields.Float(digits=(32, 2),string='Total de materiales')
    x_studio_total_de_servicios = fields.Float(digits=(32, 2),string='Total de servicios')
    x_studio_costos_indirectos = fields.Float(digits=(32, 2),string='Costos indirectos')
    x_studio_costo_total = fields.Float(digits=(32, 2),string='Costo total')
    x_studio_precio_de_venta_bom = fields.Float(digits=(32, 2),string='Precio de venta')
    x_studio_descuento_bom = fields.Float(digits=(32, 2),string='Descuento')
    x_studio_utilidad_en_mxn_bom = fields.Float(digits=(32, 2),string='Utilidad en MXN')
    x_studio_utilidad_porcentual_bom = fields.Float(digits=(32, 2),string='Utilidad en %')
    
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
            
            
class CostoMrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    x_studio_costo = fields.Monetary(related='product_id.standard_price')