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

class ProductectaChannel(models.Model):

    _name = 'producteca.channel'
    _description = 'Producteca Channel'

    name = fields.Char(string="Name",required=True,index=True)
    code = fields.Char(string="Code",help="Code Prefix for Orders: (ML for MercadoLibre) SHO (Shopify)")
    app_id = fields.Char(string="App Id",required=True,index=True)
    country_id = fields.Many2one("res.country",string="Country",index=True)
    journal_id = fields.Many2one( "account.journal", string="Journal")
    partner_id = fields.Many2one( "res.partner", string="Partner")

class ProductectaChannelBinding(models.Model):

    _name = 'producteca.channel.binding'
    _description = 'Producteca Channel Binding'

    configuration_id = fields.Many2one("producteca.configuration",string="Configuration")
    channel_id = fields.Many2one("producteca.channel",string="Producteca Channel")
    name = fields.Char(string="Name",required=True,index=True)
    code = fields.Char(string="Code",help="Code Prefix for Orders: (ML for MercadoLibre) SHO (Shopify)")
    app_id = fields.Char(string="App Id",related="channel_id.app_id",index=True)
    country_id = fields.Many2one("res.country",string="Country",index=True)
    journal_id = fields.Many2one( "account.journal", string="Journal")
    payment_journal_id = fields.Many2one( "account.journal", string="Payment Journal")
    partner_id = fields.Many2one( "res.partner", string="Partner")
    partner_account_receive_id = fields.Many2one( "account.account", string="Cuenta a cobrar (partner)")
    account_payment_receiptbook_id = fields.Many2one( "account.payment.receiptbook", string="Recibos")
    account_payment_receipt_validation = fields.Selection([('draft','Borrador'),('validate','Autovalidación')], string="Payment validation",default='draft')
    #partner_account_send_id = fields.Many2one( "account.account", string="Cuenta a pagar (partner)")
    #sequence_id = fields.Many2one('ir.sequence', string='Order Sequence',
    #    help="Order labelling for this channel", copy=False)

    analytic_account_id = fields.Many2one("account.analytic.account",string="Cuenta Analitica")
    l10n_mx_edi_usage = fields.Char(string="Uso",default="G03")
    l10n_mx_edi_payment_method_id = fields.Many2one("l10n_mx_edi.payment.method",string="Forma de pago")


class ProductecaConnectionConfiguration(models.Model):

    _name = "producteca.configuration"
    _description = "Producteca Connection Parameters Configuration"
    _inherit = "ocapi.connection.configuration"

    producteca_channels = fields.Many2many("producteca.channel", string="Producteca Channels")
    producteca_channels_bindings = fields.One2many("producteca.channel.binding", "configuration_id", string="Producteca Channels Bindings")

    accounts = fields.One2many( "producteca.account","configuration", string="Accounts", help="Accounts"  )


    #Import

    #import_payments_customer = fields.Boolean(string="Import Payments Customer")
    import_payments_fee = fields.Boolean(string="Import Payments Fee")
    import_payments_shipment = fields.Boolean(string="Import Payments Shipment")

    doc_undefined = fields.Char(string="DNI Consumidor final indefinido")


    #doc_type_undefined = fields.Char(string="Doc Tipo indefinido")
    import_price_lists = fields.Many2many("product.pricelist",relation='producteca_conf_import_pricelist_rel',column1='configuration_id',column2='pricelist_id',string="Import Price Lists")

    #Publish


    #stock warehouse
    #publish location
