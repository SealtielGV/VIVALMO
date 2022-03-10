from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    x_studio_pr_relacionada = fields.Many2one('project.task',string='PR relacionada')
    production_id = fields.Many2one('mrp.production',string='MO')
    production_status = fields.Selection(related='production_id.state')
    location_id = fields.Many2one('stock.location',string='Ubicación',related='stock_move_id.location_id')
    
    
    @api.model
    def create(self,vals):
        res = super(VivalmoStockValuationLayer,self).create(vals)
        if res.stock_move_id and res.stock_move_id.raw_material_production_id:
            res.update({
                'x_studio_pr_relacionada': res.stock_move_id.raw_material_production_id.x_studio_pr.id,
                'production_id': res.stock_move_id.raw_material_production_id.id
            }) 
        return res 
    