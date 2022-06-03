from odoo import models, fields, api, _

class VivalmoMrpProduction(models.Model):
    _inherit = 'mrp.production'


    x_studio_pr = fields.Many2one('project.task',string='PR')
    x_studio_cantidad_producida = fields.Float(readonly=True, compute='_compute_x_studio_cantidad_producida', store=True)


    @api.depends('scrap_ids')
    def _compute_x_studio_cantidad_producida(self):
        if len(self.scrap_ids) > 0:
            scrap = 0.00
            for sq in self.scrap_ids:
                scrap += sq.scrap_qty
            for record in self:
                record.x_studio_cantidad_producida = record.product_qty - scrap


    def button_mark_done(self):
        super(VivalmoMrpProduction,self).button_mark_done()
        self.x_studio_cantidad_producida = self.product_qty
        return True