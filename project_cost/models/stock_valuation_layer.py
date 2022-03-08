from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    x_studio_pr_relacionada = fields.Many2one('project.task',string='PR relacionada', related="stock_move_id.task_id")
    production_id = fields.Many2one('mrp.production',string='MO')