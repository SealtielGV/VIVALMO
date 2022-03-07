from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    
    task_id = fields.Many2one('project.task',string='Tarea')
        
        
    def action_validate(self):
        res = super(VivalmoStockScrap).action_validate()
        if self.production_id and self.production.x_studio_pr:
            self.task_id = self.production.x_studio_pr
        else:
            self.task_id = False
        return res

    