from odoo import models, fields, api, _
from odoo.exceptions import UserError

class VivalmoMrpProduction(models.Model):
    _inherit = 'mrp.production'


    x_studio_pr = fields.Many2one('project.task',string='PR')