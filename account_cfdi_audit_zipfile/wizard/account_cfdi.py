# -*- encoding: utf-8 -*-

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from odoo import api, exceptions, fields, models, _
#import odoo.addons.decimal_precision as dp
import time
from datetime import datetime, timedelta
import base64
import os
import zipfile
import subprocess
import tempfile
from xml.dom.minidom import parse, parseString
from suds.client import Client
from lxml import etree
from lxml.objectify import fromstring


import logging

_logger = logging.getLogger(__name__)


 
class AccountCFDItWizardLinkCfdi(models.TransientModel):
    _name = 'account.cfdi.wizard.link.cfdi'
    _description = 'Wizard assiociate cfdi in exist invoice'
    #current_cfdi 
    #current_file 
    subtotal   = fields.Float(string="SubTotal", digits=(18,2))
    invoice_id_search = fields.Many2one('account.move', 
        string="Factura", copy=False,
        domain="[('l10n_mx_edi_cfdi_uuid','=',False),('partner_id.vat','=',rfc),('state','!=','cancel'),('move_type','=','in_invoice')]")   
    invoice_ids = fields.Many2many('account.move', 'account_cfdi_link_rel', 'link_id', 'invoice_id', string="Invoices", copy=False,
                                   help="""Technical field containing the invoice for which the payment has been generated.
                                   This does not especially correspond to the invoices reconciled with the payment,
                                   as it can have been generated first, and reconciled later""")                

    attachment_ids = fields.Many2many(
        string = 'Documentos',
        comodel_name='ir.attachment',
        relation='cfdi_wizard_attachment_document',
    )
    rfc = fields.Char('RFC')
    equal = fields.Boolean('Igual')

    

    def associate_xml(self):
        attachment = self.env['ir.attachment'].create({
            'name': self.attachment_ids.name,
            'datas': self.attachment_ids.datas,
            'res_model':'account.move',
            'res_id': self.invoice_id_search.id,
            'res_name': self.name_get()[0][1]
        })
        _logger.info('Documento = '+str(attachment.id))
        return {'type': 'ir.actions.act_window_close'}
    
    @api.onchange('invoice_id_search')
    def review_total_xml(self):
        if self.invoice_id_search:
            base = base64.decodestring(self.attachment_ids[0].datas).lower()
            xml_value = parseString(base)
            comprobante = xml_value.getElementsByTagName('cfdi:comprobante')[0]
            total = float(comprobante.attributes['total'].value)*-1
            
            if self.invoice_id_search.amount_total_signed != total:
                self.equal = True
            else:
                self.equal = False
            
            
            
       
        
    def on_cancel(self):
        return {'type': 'ir.actions.act_window_close'}   