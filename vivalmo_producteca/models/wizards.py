# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo import api, models, fields
import logging

_logger = logging.getLogger(__name__)
from odoo.addons.odoo_connector_api_producteca.models.versions import *

class InvoiceOpenSign(models.TransientModel):

    _name = "vivalmo.producteca.invoice.wiz"
    _description = "Wizard de validacion masiva de facturas"

    #connectors = fields.Many2many("ocapi.connection.account", string='Connectors')
    open_invoice = fields.Boolean(string="Publicar / Open",default=True)
    sign_invoice = fields.Boolean(string="Timbrar / Sign",default=True)
    
    def invoice_process(self, context=None):

        context = context or self.env.context

        _logger.info("invoice_process")

        company = self.env.user.company_id
        invoice_ids = context['active_ids']
        invoice_obj = self.env[acc_inv_model]
        res = {}
        for invoice_id in invoice_ids:
            invoice = invoice_obj.browse(invoice_id)
            if invoice:
                _logger.info("Processing invoice: "+str(invoice.name))
                if self.open_invoice:
                    invoice.action_post()
                if self.sign_invoice:
                    invoice.action_process_edi_web_services()

            
            