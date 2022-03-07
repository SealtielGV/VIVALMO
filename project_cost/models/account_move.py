from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoAccountMove(models.Model):
    _inherit = 'account.move'

    x_studio_orden_de_fabricacion_pr = fields.Many2one('project.task',string="Tarea")