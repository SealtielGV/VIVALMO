from odoo import models, fields, api, _
from odoo.exceptions import UserError

import logging
_logger = logging.getLogger(__name__)



class MrpBomCostTotal(models.Model):
    _inherit = 'mrp.bom'
    
    
    x_studio_total_de_materiales = fields.Float(digits=(32, 2),string='Total de materiales',compute='_compute_total_materiales_costo')
    x_studio_total_de_servicios = fields.Float(digits=(32, 2),string='Total de servicios',compute='_compute_total_servicios')
    x_studio_costos_indirectos = fields.Float(digits=(32, 2),string='Costos indirectos')
    x_studio_costo_total = fields.Float(digits=(32, 2),string='Costo producción',compute='_compute_total_costo')
    x_studio_precio_de_venta_bom = fields.Float(digits=(32, 2),string='Precio de venta')
    x_studio_descuento_bom = fields.Float(digits=(32, 2),string='Descuento')
    x_studio_utilidad_en_mxn_bom = fields.Float(digits=(32, 2),string='Utilidad en MXN',compute='_compute_total_utilidad')
    x_studio_utilidad_porcentual_bom = fields.Float(digits=(32, 2),string='Utilidad en %',compute='_compute_porcentaje_utilidad')
    x_studio_se00001_servicio_de_corte = fields.Float(digits=(32, 2),string='SE00001 Servicio de corte')
    x_studio_se00002_servicio_de_bordado = fields.Float(digits=(32, 2),string='SE00002 Servicio de bordado')
    x_studio_se00003_servicio_de_costura = fields.Float(digits=(32, 2),string='SE00003 Servicio de costura')
    x_studio_se00004_servicio_de_lavado = fields.Float(digits=(32, 2),string='SE00004 Servicio de lavado')
    x_studio_se00005_servicio_de_terminado = fields.Float(digits=(32, 2),string='SE00005 Servicio de terminado')
    
    ##new_fields
    net_price = fields.Float(digits=(32, 2),string='Precio neto',compute='_compute_net_price')
    marketplace_cost = fields.Float(digits=(32, 2),string='Costo logístico marketplace')
    marketplace_porcentage_commission = fields.Float(digits=(32, 2),string='Porcentaje comisión marketplace')
    marketplace_commission = fields.Float(digits=(32, 2),string='Costo comisión marketplace',compute='_compute_bom_comission_marketplace')
    
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
            bom.x_studio_costo_total = bom.x_studio_total_de_materiales + bom. x_studio_total_de_servicios + bom. x_studio_costos_indirectos
            
            
    @api.depends('net_price','x_studio_costo_total','marketplace_cost','marketplace_commission','x_studio_canal_de_venta')
    def _compute_total_utilidad(self):
        for bom in self:
            amount = bom.net_price - bom.x_studio_costo_total
            if bom.x_studio_canal_de_venta != 'PRICE SHOES':
                amount = bom.net_price - bom.x_studio_costo_total -bom.marketplace_cost - bom.marketplace_commission
            bom.x_studio_utilidad_en_mxn_bom = amount
            
            
    @api.depends('x_studio_utilidad_en_mxn_bom','net_price')
    def _compute_porcentaje_utilidad(self):
        for bom in self:
            bom.x_studio_utilidad_porcentual_bom = bom.x_studio_utilidad_en_mxn_bom/bom.net_price if bom.x_studio_utilidad_en_mxn_bom > 0 else 0
    
    @api.depends('x_studio_precio_de_venta_bom','x_studio_descuento_bom')
    def _compute_net_price(self):
        for bom in self:
            
            bom.net_price = bom.x_studio_precio_de_venta_bom * (1-bom.x_studio_descuento_bom)
    
          
    @api.depends('net_price','marketplace_porcentage_commission')
    def _compute_bom_comission_marketplace(self)  :
        for bom in self:
            bom.marketplace_commission = bom.net_price * bom.marketplace_porcentage_commission
    
    def convert_value(self, value):
        if value == False:
            return ''
        else:
            return str(value)
        
    @api.onchange('x_studio_canal_de_venta')
    def onchange_marketplace_values(self):
        if self.x_studio_canal_de_venta == 'PRICE SHOES':
            self.marketplace_porcentage_commission = 0
            self.marketplace_cost = 0
            
    def write(self,vals):
        
        message = "<span>Se han modificado los siguientes campos: <span> <ul>"
        if 'code' in vals:
            message+="<li>Hoja de costo: "+self.convert_value(self.code)+"--->"+self.convert_value(vals['code'])+"</li>"
        if 'x_studio_temporada' in vals:
            message+="<li>Temporada: "+self.convert_value(self.x_studio_temporada)+"--->"+self.convert_value(vals['x_studio_temporada']) +"</li>"
        if 'x_studio_canal_de_venta' in vals:
            message+="<li>Canal de venta: "+self.convert_value(self.x_studio_canal_de_venta)+"--->"+self.convert_value(vals['x_studio_canal_de_venta']) +"</li>"
        if 'product_tmpl_id' in vals:
            product =  self.env['product.template'].search([('id','=',vals['product_tmpl_id'])]).name
            message+="<li>Modelo: "+self.convert_value(self.product_tmpl_id.name)+"--->"+self.convert_value(product) +"</li>"
        if 'x_studio_color' in vals:
            attributes = self.env['product.attribute.value'].search([('id','in',vals['x_studio_color'][0][2])]).mapped('name')
            message+="<li>Color: "+','.join(self.x_studio_color.mapped('name')) +"--->"+','.join(attributes)+"</li>"
        if 'x_studio_fit' in vals:
            attributes = self.env['product.attribute.value'].search([('id','in',vals['x_studio_fit'][0][2])]).mapped('x_studio_color_lavado')
            message+="<li>Fit: "+','.join(self.x_studio_fit.mapped('x_studio_color_lavado'))+"--->"+','.join(attributes)+"</li>"
        if 'x_studio_estilos_bom' in vals:
            attributes = self.env['product.attribute.value'].search([('id','in',vals['x_studio_estilos_bom'][0][2])]).mapped('name')
            message+="<li>Estilos: "+','.join(self.x_studio_estilos_bom.mapped('name'))+"--->"+','.join(attributes)  +"</li>"
        if 'x_studio_instrucciones_de_lavado' in vals:
            attributes = self.env['product.attribute.value'].search([('id','in',vals['x_studio_instrucciones_de_lavado'][0][2])]).mapped('x_studio_color_lavado')
            message+="<li>Instrucciones de labado húmedos : "+','.join(self.x_studio_instrucciones_de_lavado.mapped('x_studio_color_lavado'))+"--->"+','.join(attributes) +"</li>"
        if 'x_studio_instrucciones_de_lavado_secos' in vals:
            attributes = self.env['product.attribute.value'].search([('id','in',vals['x_studio_instrucciones_de_lavado_secos'][0][2])]).mapped('x_studio_color_lavado')
            message+="<li>Instrucciones de labado secos : "+','.join(self.x_studio_instrucciones_de_lavado_secos.mapped('x_studio_color_lavado')) +"--->"+','.join(attributes)+"</li>"
        if 'x_studio_segmento' in vals:            
            message+="<li>Segmento : "+self.convert_value(self.x_studio_segmento)+"--->"+self.convert_value(vals['x_studio_segmento']) +"</li>"
        if 'x_studio_tallas_a_fabricar' in vals:
            attributes = self.env['product.attribute.value'].search([('id','in',vals['x_studio_tallas_a_fabricar'][0][2])]).mapped('name')
            message+="<li>Tallas a fabricar: "+','.join(self.x_studio_tallas_a_fabricar.mapped('name')) +"--->"+','.join(attributes)+"</li>"
        if 'product_qty' in vals:
            message+="<li>Cantidad : "+self.convert_value(self.product_qty)+"--->"+self.convert_value(vals['product_qty']) +"</li>"
        if 'x_studio_fotografa' in vals:
            message+="<li>Fotografía: Se cambio la fotografía</li>"
        if 'company_id' in vals:
            company = self.env['res.company'].sudo().search([('id','=',vals['company_id'])]).name
            message+="<li>Fabricante: "+self.convert_value(self.company_id.name)+"--->"+self.convert_value(company) +"</li>"
        if 'x_studio_disenador_bom' in vals:
            message+="<li>Diseñador: "+self.convert_value(self.x_studio_disenador_bom.name)+"--->"+self.convert_value(vals['x_studio_disenador_bom']) +"</li>"
        if 'type' in vals:
            message+="<li>Tipo de LdM: "+self.convert_value(self.type)+"--->"+self.convert_value(vals['type']) +"</li>"
        if 'x_studio_total_de_materiales' in vals:
            message+="<li>Total de materiales: "+self.convert_value(self.x_studio_total_de_materiales)+"--->"+self.convert_value(vals['x_studio_total_de_materiales']) +"</li>"
        if 'x_studio_total_de_servicios' in vals:
            message+="<li>Total de servicios: "+self.convert_value(self.x_studio_total_de_servicios)+"--->"+self.convert_value(vals['x_studio_total_de_servicios']) +"</li>"
        if 'x_studio_costos_indirectos' in vals:
            message+="<li>Costos indirectos: "+self.convert_value(self.x_studio_costos_indirectos)+"--->"+self.convert_value(vals['x_studio_costos_indirectos']) +"</li>"
        if 'x_studio_costo_total' in vals:
            message+="<li>Costos Producción: "+self.convert_value(self.x_studio_costo_total)+"--->"+self.convert_value(vals['x_studio_costo_total']) +"</li>"
        if 'x_studio_precio_de_venta_bom' in vals:
            message+="<li>Precio de venta: "+self.convert_value(self.x_studio_precio_de_venta_bom)+"--->"+self.convert_value(vals['x_studio_precio_de_venta_bom']) +"</li>"
        if 'x_studio_descuento_bom' in vals:
            message+="<li>Descuento: "+self.convert_value(self.x_studio_descuento_bom)+"--->"+self.convert_value(vals['x_studio_descuento_bom']) +"</li>"
        
        if 'net_price' in vals:
            message+="<li>Precio neto: "+self.convert_value(self.net_price)+"--->"+self.convert_value(vals['net_price']) +"</li>"
        
        if 'marketplace_cost' in vals:
            message+="<li>Costo logístico marketplace: "+self.convert_value(self.marketplace_cost)+"--->"+self.convert_value(vals['marketplace_cost']) +"</li>"
            
        if 'marketplace_porcentage_commission' in vals:
            message+="<li>Porcentaje comisión marketplace: "+self.convert_value(self.marketplace_porcentage_commission)+"--->"+self.convert_value(vals['marketplace_porcentage_commission']) +"</li>"

        if 'marketplace_commission' in vals:
            message+="<li>Costo comisión marketplace: "+self.convert_value(self.marketplace_commission)+"--->"+self.convert_value(vals['marketplace_commission']) +"</li>"
            
        if 'x_studio_utilidad_en_mxn_bom' in vals:
            message+="<li>Utilidad en MXN: "+self.convert_value(self.x_studio_utilidad_en_mxn_bom)+"--->"+self.convert_value(vals['x_studio_utilidad_en_mxn_bom']) +"</li>"
        if 'x_studio_utilidad_porcentual_bom' in vals:
            message+="<li>Utilidad en %: "+self.convert_value(self.x_studio_utilidad_porcentual_bom)+"--->"+self.convert_value(vals['x_studio_utilidad_porcentual_bom']) +"</li>"
        if 'picking_type_id' in vals:
            picking_type = self.env['stock.picking.type'].search([('id','=',vals['picking_type_id'])]).name
            message+="<li>Operación: "+self.convert_value(self.picking_type_id.name)+"--->"+self.convert_value(picking_type) +"</li>"
        if 'consumption' in vals:
            message+="<li>Consumo: "+self.convert_value(self.consumption)+"--->"+self.convert_value(vals['consumption']) +"</li>"
        if 'x_studio_se00001_servicio_de_corte' in vals:
            message+="<li>SE00001 Servicio de Corte: "+self.convert_value(self.x_studio_se00001_servicio_de_corte)+"--->"+self.convert_value(vals['x_studio_se00001_servicio_de_corte']) +"</li>"
        if 'x_studio_se00002_servicio_de_bordado' in vals:
            message+="<li>SE00002 Servicio de bordado: "+self.convert_value(self.x_studio_se00002_servicio_de_bordado)+"--->"+self.convert_value(vals['x_studio_se00002_servicio_de_bordado']) +"</li>"
        if 'x_studio_se00003_servicio_de_costura' in vals:
            message+="<li>SE00003 Servicio de costura: "+self.convert_value(self.x_studio_se00003_servicio_de_costura)+"--->"+self.convert_value(vals['x_studio_se00003_servicio_de_costura']) +"</li>"
        if 'x_studio_se00004_servicio_de_lavado' in vals:
            message+="<li>SE00004 Servicio de lavado: "+self.convert_value(self.x_studio_se00004_servicio_de_lavado)+"--->"+self.convert_value(vals['x_studio_se00004_servicio_de_lavado']) +"</li>"
        if 'x_studio_se00005_servicio_de_terminado' in vals:
            message+="<li>SE00005 Servicio de terminado: "+self.convert_value(self.x_studio_se00005_servicio_de_terminado)+"--->"+self.convert_value(vals['x_studio_se00005_servicio_de_terminado']) +"</li>"
        if 'x_studio_instrucciones_y_comentarios_bom' in vals:
            message+="<li>Instrucciones y comentarios: "+self.convert_value(self.x_studio_instrucciones_y_comentarios_bom)+" --->"+self.convert_value(vals['x_studio_instrucciones_y_comentarios_bom']) +"</li>"
        if 'bom_line_ids' in vals:
            for line in vals['bom_line_ids']:
                if line[0] == 0:
                    message+="<li>Se ha creado el siguiente componente: <br/>"    
                    values = line[2]
                    message+= " Nuevo: <br/>" 
                    if 'product_id' in values and values != False:
                        product = self.env['product.product'].search([('id','=',values['product_id'])]).name
                        message+="<span style='tab-size:4;'>Producto: "+self.convert_value(product)+"</span>,<br/>"
                    if 'x_studio_descripcion' in  values :
                        message+="<span style='tab-size:4;'>Descripción: "+self.convert_value(values['x_studio_descripcion'])+"</span>,<br/>"
                    if 'product_qty' in  values and values != False:
                        message+="<span style='tab-size:4;'>Cantidad: "+self.convert_value(values['product_qty'])+"</span>,<br/>"
                    if 'product_uom_id' in  values and values != False:
                        message+="<span style='tab-size:4;'>Unidad: "+self.env['uom.uom'].search([('id','=',values['product_uom_id'])]).name+"</span>,<br/>"
                    if 'x_studio_costo' in  values and values != False:
                        message+="<span style='tab-size:4;'>Costo: "+self.convert_value(values['x_studio_costo'])+"</span>,<br/>"
                    if 'amaount_total' in  values and values != False:
                        message+="<span style='tab-size:4;'>Total: "+self.convert_value(values['amaount_total'])+"</span>,<br/>"
                    if 'x_studio_aplicado_en' in  values and values != False:
                        message+="<span style='tab-size:4;'>Aplicado en: "+self.convert_value(values['x_studio_aplicado_en'])+"</span><br/>"
                    message+="</li>"       
                elif line[0] == 1 and line[2] != False and ('product_id' in line[2] or 'x_studio_descripcion' in line[2] or 'product_qty' in line[2] or 'product_uom_id' in line[2] or 'x_studio_costo' in line[2] or 'amount_total' in line[2] or 'x_studio_aplicado_en' in line[2]):
                    message+="<li>Se han generado los siguientes cambios en componentes: <br/>"    
                    values = line[2]
                    bom_line = self.env['mrp.bom.line'].search([('id','=',line[1])])
                    message+= "Modificación: "+str(bom_line.x_studio_descripcion)+"<br/>"
                    if 'product_id' in values and values != False:
                        product = self.env['product.product'].search([('id','=',values['product_id'])]).name
                        message+="  Producto: "+self.convert_value(bom_line.product_id.name)+"--->"+self.convert_value(product) +"<br/>"
                    if 'x_studio_descripcion' in  values and values != False:
                        message+="  Descripción: "+self.convert_value(bom_line.x_studio_descripcion)+"--->"+self.convert_value(values['x_studio_descripcion'])+",<br/>"
                    if 'product_qty' in  values and values != False:
                        message+="  Cantidad: "+self.convert_value(bom_line.product_qty)+"--->"+self.convert_value(values['product_qty'])+",<br/>"
                    if 'product_uom_id' in  values and values != False:
                        unidad = self.env['uom.uom'].search([('id','=',values['product_uom_id'])]).name
                        message+="  Unidad: "+self.convert_value(bom_line.product_uom_id.name)+"--->"+self.convert_value(unidad)+",<br/>"
                    if 'x_studio_costo' in  values and values != False:
                        message+="  Costo: "+self.convert_value(bom_line.x_studio_costo)+"--->"+self.convert_value(values['x_studio_costo'])+",<br/>"
                    if 'amount_total' in  values and values != False:
                        message+="  Total: "+self.convert_value(bom_line.amount_total)+"--->"+self.convert_value(values['amount_total'])+",<br/>"
                    if 'x_studio_aplicado_en' in  values and values != False:
                        message+="  Aplicado en: "+self.convert_value(bom_line.x_studio_aplicado_en)+"--->"+self.convert_value(values['x_studio_aplicado_en'])+"<br/>"
                    message+="</li>"       
                elif line[0] == 2:
                    message+="<li>Se han generado los siguientes cambios en componentes: <br/>"
                    bom_line = self.env['mrp.bom.line'].search([('id','=',line[1])])
                    message+= " Eliminado registro"+str(bom_line.x_studio_descripcion)+"</li>"
                    
                else:
                    pass
                
        message  +=  "</ul></span> "
        self.message_post(body=message)
        res = super(MrpBomCostTotal, self).write(vals)
        return res
        
                  
            
class CostoMrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'
    
    x_studio_costo = fields.Float(related='product_id.standard_price')
    amount_total = fields.Float('Total',compute='compute_value_total_amount')
    

    @api.depends('x_studio_costo','product_qty')
    def compute_value_total_amount(self):
        for value in self:
            value.amount_total = value.product_qty * value.x_studio_costo
            
            
    
            
            
    