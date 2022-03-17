from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    qty_total = fields.Float(digits=(32, 2),string='Cantidad',compute='_compte_qty_total')
    
    
    @api.depends('invice_line_ids')
    def _compte_qty_total(self):
        for account in self:
            account.qty_total = sum(account.invoice_line_ids.mapped('quantity'))