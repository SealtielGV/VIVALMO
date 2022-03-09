from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    x_studio_pr_relacionada = fields.Many2one('project.task',string='PR relacionada',compute='_compute_production_value')
    production_id = fields.Many2one('mrp.production',string='MO',compute='_compute_production_value')
    
    
    @api.depends('production_id')
    def _compute_production_value(self):
        for val in self:
            val.x_studio_pr_relacionada = False
            val.production_id = False
            if val.stock_move_id.production_id:
                val.production_id = val.stock_move_id.production_id.id
                if val.stock_move_id.production_id.task_id:
                    val.x_studio_pr_relacionada = val.stock_move_id.production_id.x_studio_pr.id