from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoAccountMove(models.Model):
    _inherit = 'account.move'

    x_studio_orden_de_fabricacion_pr = fields.Many2one('project.task',string="Tarea")
    amount_tax = fields.Float(string='Impuestos',compute='_compute_total_tax')
    
    #calculo realizado para sacar el total de los impuestos
    @api.depends('amount_total_signed','amount_untaxed_signed')
    def _compute_total_tax(self):
        for tax in self:
            tax.amount_tax = tax.amount_total_signed - tax.amount_untaxed_signed
    
    