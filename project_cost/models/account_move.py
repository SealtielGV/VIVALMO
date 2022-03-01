from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoAccountMove(models.Model):
    _inherit = 'account.move'

    x_studio_many2one_field_rHur1 = fields.Many2one('project.task',string="Tarea")