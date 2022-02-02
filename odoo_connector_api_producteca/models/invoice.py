# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, osv, models, api
from odoo.tools.translate import _
import logging
_logger = logging.getLogger(__name__)
import pdb
from .warning import warning
import requests
import base64
from .versions import *
from odoo.exceptions import UserError, ValidationError

class Invoice(models.Model):

    _inherit = acc_inv_model

    producteca_mail = fields.Char(string="Producteca mail")
    producteca_inv_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Factura Archivo Adjunto',
        copy=False
    )
    producteca_order_binding_id = fields.Many2one( "producteca.sale_order", string="Producteca Sale Order" )

    def enviar_factura_producteca(self):

        _logger.info("Enviar factura a producteca")

        template = self.env.ref('odoo_connector_api_producteca.producteca_invoice_email_template', False )
        _logger.info(template)
        sale_order = self.env['sale.order'].search([('name','=',self.origin)], limit=1 )

        self.producteca_order_binding_id = sale_order and sale_order.producteca_bindings and sale_order.producteca_bindings[0]
        if not self.producteca_order_binding_id:
            _logger.error("Error no order binding")
            return {}

        if not self.producteca_inv_attachment_id:
            ATTACHMENT_NAME = "FACTURA "+self.display_name
            _logger.info(ATTACHMENT_NAME)
            REPORT_ID = 'nybble_l10n_ar_report_fe.report_invoice_fe_tc'
            report = self.env['ir.actions.report']._get_report_from_name(REPORT_ID)
            pdf = report.render_qweb_pdf(self.ids)
            b64_pdf = base64.b64encode(pdf[0])

            attachment = self.env['ir.attachment'].create({
                'name': ATTACHMENT_NAME,
                'type': 'binary',
                'datas': b64_pdf,
                'datas_fname': ATTACHMENT_NAME + '.pdf',
                'store_fname': ATTACHMENT_NAME,
                'res_model': acc_inv_model,
                'res_id': self.id,
                'mimetype': 'application/pdf'
            })
            if attachment:
                self.producteca_inv_attachment_id = attachment.id

        self.producteca_mail = self.producteca_mail or self.producteca_order_binding_id.mail or (self.producteca_order_binding_id.client and self.producteca_order_binding_id.client.mail)
        if not self.producteca_mail:
            _logger.error("Error no mail from binding, fix.")
            return

        archivos_ids=[]
        archivos_ids.append(self.producteca_inv_attachment_id.id)

        if template:
            template.email_from = str(self.company_id.email)
            template.attachment_ids = [(5, 0, [])]
            if archivos_ids:
                template.attachment_ids = [(6, 0, archivos_ids)]
            template.send_mail(self.id, force_send=True)
            template.attachment_ids = [(5, 0, [])]

    def producteca_fix_invoice( self, vals_list, pso ):
        if (pso and pso.channel_binding_id):
            if (not "l10n_mx_edi_usage" in vals_list[0] and "l10n_mx_edi_usage" in pso.channel_binding_id._fields):
                vals_list[0]["l10n_mx_edi_usage"] = pso.channel_binding_id.l10n_mx_edi_usage
            if (not "l10n_mx_edi_payment_method_id" in vals_list[0] and "l10n_mx_edi_payment_method_id" in pso.channel_binding_id._fields):
                vals_list[0]["l10n_mx_edi_payment_method_id"] = pso.channel_binding_id.l10n_mx_edi_payment_method_id and pso.channel_binding_id.l10n_mx_edi_payment_method_id.id

        return vals_list

    @api.model_create_multi
    def create(self, vals_list):
        _logger.info("vals_list: "+str(vals_list))
        if ( 'ref' in vals_list[0] and vals_list[0]['ref'] and "PR-" in vals_list[0]['ref'] ):
            pso = self.env["producteca.sale_order"].search([('name','like',vals_list[0]['ref'])], limit=1)
            if (pso and not 'producteca_order_binding_id' in vals_list[0]):
                vals_list[0]['producteca_order_binding_id'] =  pso.id

            if (pso):
                vals_list = self.producteca_fix_invoice( vals_list, pso )

            _logger.info("vals_list: "+str(vals_list) )
        rslt = super(Invoice, self).create(vals_list)
        _logger.info("rslt: "+str(rslt))
        return rslt
    #def action_post( self ):
    #    super( Invoice, self ).action_post()
