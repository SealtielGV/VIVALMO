from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockScrap(models.Model):
    _inherit = 'stock.scrap'
    
    
    task_id = fields.Many2one('project.task',string='Tarea')
        
    #agrega el valor a la tarea para que haga relación  
    def action_validate(self):
        res = super(VivalmoStockScrap, self).action_validate()
        if self.production_id and self.x_studio_pr:
            self.task_id = self.x_studio_pr
        else:
            self.task_id = False
        return res

    
