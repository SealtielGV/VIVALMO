from odoo import models, fields, api, _

class VivalmoMrpProduction(models.Model):
    _inherit = 'mrp.production'


    x_studio_pr = fields.Many2one('project.task',string='PR')
    x_studio_cantidad_producida = fields.Float(string='Cantidad Producida', readonly=True, compute='_compute_x_studio_cantidad_producida', store=True)
    scrap_qty = fields.Float(string='Cantidad Desecho', default = 0.00, readonly=True, cumpute='_compute_x_studio_cantidad_producida')

    @api.depends('scrap_ids','scrap_ids.scrap_qty')
    def _compute_x_studio_cantidad_producida(self):
        for record in self:
            if len(record.scrap_ids) > 0:
                scrap = 0.00
                for sq in record.scrap_ids:
                    scrap += sq.scrap_qty
                record.x_studio_cantidad_producida = record.product_qty - scrap
                record.scrap_qty = scrap


    def button_mark_done(self):
        super(VivalmoMrpProduction,self).button_mark_done()
        self.x_studio_cantidad_producida = self.product_qty
        return True