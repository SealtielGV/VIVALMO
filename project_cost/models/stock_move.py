from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockMove(models.Model):
    _inherit = 'stock.move'

    task_id = fields.Many2one('project.task',string='Tarea',)