from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoStockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    x_studio_pr_relacionada = fields.Many2one('project.task',string='PR relacionada')