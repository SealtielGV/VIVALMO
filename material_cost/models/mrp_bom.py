from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



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
            
    def convert_value(self, value):
        if value == False:
            return ''
        else:
            return value
            
    def write(self,vals):
        res = super(MrpBomCostTotal, self).write(vals)
        message = "<span>Se han modidicado los siguientes campos: <span> <ul>"
        if 'code' in vals:
            message+="<li>Hoja de costo: "+self.convert_value(self.code) +"</li>"
        if 'x_studio_temporada' in vals:
            message+="<li>Temporada: "+self.convert_value(self.x_studio_temporada) +"</li>"
        if 'x_studio_canal_de_venta' in vals:
            message+="<li>Canal de venta: "+self.convert_value(self.x_studio_canal_de_venta) +"</li>"
        if 'product_tmpl_id' in vals:
            message+="<li>Modelo: "+self.convert_value(self.product_tmpl_id.name) +"</li>"
        if 'x_studio_color' in vals:
            message+="<li>Color: "+','.join(self.x_studio_color.mapped('name')) +"</li>"
        if 'x_studio_fit' in vals:
            message+="<li>Fit: "+','.join(self.x_studio_fit.mapped('x_studio_color_lavado'))+"</li>"
        if 'x_studio_estilos_bom' in vals:
            message+="<li>Estilos: "+','.join(self.x_studio_estilos_bom.mapped('name')) +"</li>"
        if 'x_studio_instrucciones_de_lavado' in vals:
            message+="<li>Instrucciones de labado húmedos : "+','.join(self.x_studio_instrucciones_de_lavado.mapped('x_studio_color_lavado')) +"</li>"
        if 'x_studio_instrucciones_de_lavado_secos' in vals:
            message+="<li>Instrucciones de labado secos : "+','.join(self.x_studio_instrucciones_de_lavado_secos.mapped('x_studio_color_lavado')) +"</li>"
        if 'x_studio_segmento' in vals:            
            message+="<li>Segmento : "+self.convert_value(self.x_studio_segmento) +"</li>"
        if 'x_studio_tallas_a_fabricar' in vals:
            message+="<li>Tallas a fabricar: "+','.join(self.x_studio_instrucciones_de_lavado_secos.mapped('x_studio_color_lavado')) +"</li>"
        if 'product_qty' in vals:
            message+="<li>Cantidad : "+self.convert_value(self.product_qty) +"</li>"
        if 'x_studio_fotografa' in vals:
            message+="<li>Fotografía: Se cambio la fotografía</li>"
        if 'company_id' in vals:
            message+="<li>Fabricante: "+self.convert_value(self.company_id.name) +"</li>"
        if 'x_studio_disenador_bom' in vals:
            message+="<li>Diseñador: "+self.convert_value(self.x_studio_disenador_bom.name) +"</li>"
        if 'type' in vals:
            message+="<li>Tipo de LdM: "+self.convert_value(self.type) +"</li>"
        if 'x_studio_total_de_materiales' in vals:
            message+="<li>Total de materiales: "+self.convert_value(self.x_studio_total_de_materiales) +"</li>"
        if 'x_studio_total_de_servicios' in vals:
            message+="<li>Total de servicios: "+self.convert_value(self.x_studio_total_de_servicios) +"</li>"
        if 'x_studio_costos_indirectos' in vals:
            message+="<li>Costos indirectos: "+self.convert_value(self.x_studio_costos_indirectos) +"</li>"
        if 'x_studio_costo_total' in vals:
            message+="<li>Costos indirectos: "+self.convert_value(self.x_studio_costo_total) +"</li>"
        if 'x_studio_precio_de_venta_bom' in vals:
            message+="<li>Precio de venta: "+self.convert_value(self.x_studio_precio_de_venta_bom) +"</li>"
        if 'x_studio_descuento_bom' in vals:
            message+="<li>Descuento: "+self.convert_value(self.x_studio_descuento_bom) +"</li>"
        if 'x_studio_utilidad_en_mxn_bom' in vals:
            message+="<li>Utilidad en MXN: "+self.convert_value(self.x_studio_utilidad_en_mxn_bom) +"</li>"
        if 'x_studio_utilidad_porcentual_bom' in vals:
            message+="<li>Utilidad en %: "+self.convert_value(self.x_studio_utilidad_porcentual_bom) +"</li>"
        if 'picking_type_id' in vals:
            message+="<li>Operación: "+self.convert_value(self.picking_type_id.name) +"</li>"
        if 'consumption' in vals:
            message+="<li>Consumo: "+self.convert_value(self.consumption) +"</li>"
        if 'x_studio_se00001_servicio_de_corte' in vals:
            message+="<li>SE00001 Servicio de Corte: "+self.convert_value(self.x_studio_se00001_servicio_de_corte) +"</li>"
        if 'x_studio_se00002_servicio_de_bordado' in vals:
            message+="<li>SE00002 Servicio de bordado: "+self.convert_value(self.x_studio_se00002_servicio_de_bordado) +"</li>"
        if 'x_studio_se00003_servicio_de_costura' in vals:
            message+="<li>SE00003 Servicio de costura: "+self.convert_value(self.x_studio_se00003_servicio_de_costura) +"</li>"
        if 'x_studio_se00004_servicio_de_lavado' in vals:
            message+="<li>SE00004 Servicio de lavado: "+self.convert_value(self.x_studio_se00004_servicio_de_lavado) +"</li>"
        if 'x_studio_se00005_servicio_de_terminado' in vals:
            message+="<li>SE00005 Servicio de terminado: "+self.convert_value(self.x_studio_se00005_servicio_de_terminado) +"</li>"
        if 'x_studio_instrucciones_y_comentarios_bom' in vals:
            message+="<li>Instrucciones y comentarios: "+self.convert_value(self.x_studio_instrucciones_y_comentarios_bom) +"</li>"
        if 'bom_line_ids' in vals:
            for line in vals['bom_line_ids']:
                message+="<li>Se han generado los siguientes cambios en componentes: <br/>"
                if line[0] != 2 and line[3] != False:
                    values = line[2]
                    _logger.info(values)
                    message+= "Nuevo: <br/>" if line[0] == 0 else "Modificación: en id "+str(line[1])+"<br/>"
                    if 'product_id' in values and values != False:
                        message+="Producto: "+self.env['product.product'].search([('id','=',values['product_id'])]).name+"<br/>"
                    if 'x_studio_descripcion' in  values and values != False:
                        message+="Descripción: "+values['x_studio_descripcion']+",<br/>"
                    if 'product_qty' in  values and values != False:
                        message+="Cantidad: "+values['product_qty']+",<br/>"
                    if 'product_uom_id' in  values and values != False:
                        message+="Unidad: "+self.env['uom.uom'].search([('id','=',values['product_uom_id'])]).name+",<br/>"
                    if 'x_studio_costo' in  values and values != False:
                        message+="Costo: "+values['x_studio_costo']+",<br/>"
                    if 'amaount_total' in  values and values != False:
                        message+="Total: "+values['amaount_total']+",<br/>"
                    if 'x_studio_aplicado_en' in  values and values != False:
                        message+="Aplicado en: "+values['x_studio_aplicado_en']+"<br/>"
                else:
                    message+= "Eliminado registro con id "+str(line[1])
                message+="</li>"
        message  +=  "</ul></span> "
        self.message_post(body=message)
        return res
        
        
                  
            
class CostoMrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    x_studio_costo = fields.Float(related='product_id.standard_price')
    amount_total = fields.Float('Total',compute='compute_value_total_amount')
    

    @api.depends('x_studio_costo','product_qty')
    def compute_value_total_amount(self):
        for value in self:
            value.amount_total = value.product_qty * value.x_studio_costo
            
            
    
            
            
    