from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockMove(models.Model):
    _inherit = 'stock.move'

    task_id = fields.Many2one('project.task',string='Tarea',)
    
    
    def write(self,vals):
        res = super(VivalmoStockMove, self).write(vals)
        if self.raw_material_production_id and self.stock_valuation_layer_ids.filtered(lambda s: s.production_id == False):
            for valuation in self.stock_valuation_layer_ids:
                if self.raw_material_production_id.x_studio_pr:
                    valuation.update({
                        'x_studio_pr_relacionada':self.raw_material_production_id.x_studio_pr.id,
                        'production_id': self.raw_material_production_id.id
                    })
                else:
                    valuation.update({
                        'production_id': self.raw_material_production_id.id
                    })
                    
        return res