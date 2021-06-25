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
import operator as py_operator

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class ProductecaConnectionBinding(models.Model):

    _name = "producteca.binding"
    _description = "Producteca Connection Binding"
    _inherit = "ocapi.connection.binding"

    #Connection reference defining mkt place credentials
    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )


class ProductecaConnectionBindingProductTemplate(models.Model):

    _name = "producteca.binding.product_template"
    _description = "Producteca Product Binding Product Template"
    _inherit = "ocapi.connection.binding.product_template"

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )
    variant_bindings = fields.One2many( 'producteca.binding.product','binding_product_tmpl_id',string='Variant Bindings')

    def get_price_str_tmpl(self):
        prices = []
        prices_str = ""

        product_tpl = self.product_tmpl_id
        account = self.connection_account
        if not product_tpl or not account:
            return prices_str

        #self.with_context(pricelist=pricelist.id).price
        #for plitem in product.item_ids:
        for pl in account.configuration.publish_price_lists:
            plprice = product_tpl.with_context(pricelist=pl.id).price
            price = {
                "priceListId": pl.id,
                "priceList": pl.name,
                "amount": plprice,
                "currency": pl.currency_id.name
            }
            #prices.append(price)
            prices_str+= str(price["priceList"])+str(": ")+str(price["amount"])

        return prices_str

    def _calculate_price_resume_tmpl(self):
        #_logger.info("Calculate price resume")
        for bindT in self:
            #var.stock_resume = "LOEC: 5, MFULL: 3"
            bindT.price_resume_tmpl = bindT.get_price_str_tmpl()

    def get_stock_str_tmpl(self):
        stocks = []
        stocks_str = ""
        #ss = variant._product_available()

        product_tmpl = self.product_tmpl_id
        account = self.connection_account
        if not product_tmpl or not account:
            return stocks_str

        #_logger.info("account.configuration.publish_stock_locations")
        #_logger.info(account.configuration.publish_stock_locations.mapped("id"))
        locids = account.configuration.publish_stock_locations.mapped("id")
        sq = self.env["stock.quant"].search([('product_tmpl_id','=',product_tmpl.id),('location_id','in',locids)],order="location_id asc")
        if (sq):
            #_logger.info( sq )
            #_logger.info( sq.name )
            for s in sq:
                #TODO: filtrar por configuration.locations
                #TODO: merge de stocks
                #TODO: solo publicar available
                if ( s.location_id.usage == "internal"):
                    _logger.info( s )
                    sjson = {
                        "warehouseId": s.location_id.id,
                        "warehouse": s.location_id.display_name,
                        "quantity": s.quantity,
                        "reserved": s.reserved_quantity,
                        "available": s.quantity - s.reserved_quantity
                    }
                    #stocks.append(sjson)
                    stocks_str+= str(sjson["warehouse"])+str(": ")+str(sjson["quantity"])+str("/")+str(str(sjson["available"]))
                    stocks_str+= " "
        return stocks_str

    def _calculate_stock_resume_tmpl(self):
        #_logger.info("Calculate stock resume")
        for bindT in self:
            bindT.stock_resume_tmpl = "LOEC: 5, MFULL: 3"
            bindT.stock_resume_tmpl = bindT.get_stock_str_tmpl()


    stock_resume_tmpl = fields.Char(string="Stock Resumen Tmpl", compute="_calculate_stock_resume_tmpl", store=False )
    price_resume_tmpl = fields.Char(string="Price Resumen Tmpl", compute="_calculate_price_resume_tmpl", store=False )
    product_tmpl_company = fields.Many2one(related="product_tmpl_id.company_id",string="Company",store=True,index=True)


class ProductecaConnectionBindingProductVariant(models.Model):

    _name = "producteca.binding.product"
    _description = "Producteca Product Binding Product"
    _inherit = ["producteca.binding.product_template","ocapi.connection.binding.product"]

    binding_product_tmpl_id = fields.Many2one("producteca.binding.product_template",string="Product Template Binding")

    def get_price_str(self):
        prices = []
        prices_str = ""

        variant = self.product_id
        account = self.connection_account
        if not variant or not account:
            return prices_str

        #self.with_context(pricelist=pricelist.id).price
        #for plitem in product.item_ids:
        for pl in account.configuration.publish_price_lists:
            plprice = variant.with_context(pricelist=pl.id).price
            price = {
                "priceListId": pl.id,
                "priceList": pl.name,
                "amount": plprice,
                "currency": pl.currency_id.name
            }
            #prices.append(price)
            prices_str+= str(price["priceList"])+str(": ")+str(price["amount"])
            self.price = plprice

        return prices_str

    def _calculate_price_resume(self):
        #_logger.info("Calculate price resume")
        for var in self:
            #var.stock_resume = "LOEC: 5, MFULL: 3"
            var.price_resume = var.get_price_str()

    def get_stock_str(self):
        stocks = []
        stocks_str = ""
        stocks_on_hand = 0.0
        stocks_available = 0.0
        #ss = variant._product_available()

        variant = self.product_id
        account = self.connection_account
        if not variant or not account:
            return stocks_str

        #_logger.info("account.configuration.publish_stock_locations")
        #_logger.info(account.configuration.publish_stock_locations.mapped("id"))
        locids = account.configuration.publish_stock_locations.mapped("id")
        sq = self.env["stock.quant"].search([('product_id','=',variant.id),('location_id','in',locids)],order="location_id asc")
        if (sq):
            #_logger.info( sq )
            #_logger.info( sq.name )
            for s in sq:
                #TODO: filtrar por configuration.locations
                #TODO: merge de stocks
                #TODO: solo publicar available
                if ( s.location_id.usage == "internal"):
                    _logger.info( s )
                    sjson = {
                        "warehouseId": s.location_id.id,
                        "warehouse": s.location_id.display_name,
                        "quantity": s.quantity,
                        "reserved": s.reserved_quantity,
                        "available": s.quantity - s.reserved_quantity
                    }
                    #stocks.append(sjson)
                    stocks_str+= str(sjson["warehouse"])+str(": ")+str(sjson["quantity"])+str("/")+str(str(sjson["available"]))
                    stocks_str+= " "
                    stocks_on_hand+= sjson["quantity"]
                    stocks_available+= sjson["available"]
                    #variant.stock = sjson["available"]

        return stocks_str, stocks_on_hand, stocks_available

    def _calculate_stock_resume(self):
        #_logger.info("Calculate stock resume")
        for var in self:
            var.stock_resume = ""
            stocks_str, stocks_on_hand, stocks_available = var.get_stock_str()
            var.stock_resume = stocks_str
            var.stock_resume_on_hand = stocks_on_hand
            var.stock_resume_available = stocks_available

    def _calculate_code_resume( self ):
        for var in self:
            var.code_resume = (var.product_id and var.product_id.barcode) or ""
            var.barcode = (var.product_id and var.product_id.barcode) or ""
            var.sku = (var.product_id and var.product_id.default_code) or ""

    stock_resume = fields.Char(string="Stock Resumen", compute="_calculate_stock_resume", store=False )
    price_resume = fields.Char(string="Price Resumen", compute="_calculate_price_resume", store=False )
    code_resume = fields.Char(string="Codes",compute="_calculate_code_resume", store=False)

    price = fields.Float(string="Price", compute="_calculate_price_resume", store=False)


    def _search_stock_resume_on_hand(self, operator, value):
        ids = []
        if (operator == '>' or operator == '<' or operator == '=' or operator == '>=' or operator == '<='):

            company = self.env.user.company_id
            account = company.producteca_connections and company.producteca_connections[0]
            if not account:
                return []

            locids = account.configuration.publish_stock_locations.mapped("id")
            sq = self.env["stock.quant"].search([('location_id','in',locids),('quantity',operator,value)],order="quantity asc")
            if sq:
                pids = sq.mapped("product_id")
                vbids = self.search([('product_id','in', pids.ids)])
                if vbids:
                    ids = [('id','in',vbids.ids)]

        return ids

    def _search_stock_resume_available(self, operator, value):
        ids = []
        if (operator == '>' or operator == '<' or operator == '=' or operator == '>=' or operator == '<='):

            company = self.env.user.company_id
            account = company.producteca_connections and company.producteca_connections[0]

            if not account:
                return []
            locids = account.configuration.publish_stock_locations.mapped("id")

            rsq = self.env["stock.quant"].search([('location_id','in',locids),('reserved_quantity','>',0.0)],order="reserved_quantity asc")
            sq = self.env["stock.quant"].search([('location_id','in',locids),('quantity',operator,value)],order="quantity asc")

            pids = []

            if sq:
                products_quantity = sq.mapped("product_id")
                pids = products_quantity

            if rsq:
                products_reserved = rsq.mapped("product_id")
                pids_reserved = products_reserved.ids
                products_not_reserved = products_quantity - products_reserved
                for q in rsq:
                    qav = q.quantity - q.reserved_quantity
                    if OPERATORS[operator](qav, value):
                        products_not_reserved+= q.product_id
                pids = products_not_reserved

            if pids:
                #_logger.info(pids.ids)
                vbids = self.search([('product_id','in', pids.ids)])
                #_logger.info(vbids)
                if vbids:
                    ids = [('id','in',vbids.ids)]

        return ids

    stock_resume_on_hand = fields.Float(string="Qty On hand", compute="_calculate_stock_resume"
                        , search="_search_stock_resume_on_hand"
                        )
    stock_resume_available = fields.Float(string="Qty Available", compute="_calculate_stock_resume"
                        , search="_search_stock_resume_available"
                        )

    def _product_main_cat( self ):
        for b in self:
            b.product_main_cat = None
            b.product_main_cat_child = None
            p = b.product_id
            if p:
                child = (p.categ_id and p.categ_id.parent_id)
                main = (child and child.parent_id)
                if not main:
                    child = p.categ_id
                #down_one = (child.parent_id == False) and
                #child_is = p.categ_id and p.categ_id.parent_id
                b.product_main_cat_child = child
                b.product_main_cat = child and child.parent_id

    def _product_size_color( self ):
        for b in self:
            b.product_size = None
            b.product_color = None
            b.product_gender = None
            p = b.product_id
            if p and p.attribute_value_ids:
                for attval in p.attribute_value_ids:
                    if attval.attribute_id.name=="Size":
                        b.product_size = attval.id
                    if attval.attribute_id.name=="Color":
                        b.product_color = attval.id
                    if attval.attribute_id.name=="Género":
                        b.product_gender = attval.id

    def _search_shop( self, operator, value ):
        shops = False
        _logger.info("_search_shop:"+str(operator)+" "+str(value))
        if value:
            shops = self.env['website_sale.shop'].search([('name',operator,value)])
            _logger.info("shops:"+str(shops))
            #self.search([('product_shop', operator, value)])
        #else:
        #    shops = self.env['website_sale.shop'].search([('name',operator,value)])
            #packs = self.search([('quant_ids', operator, value)])
            res = []
        if shops:
            res = [('product_shop', 'in', shops.ids)]
        else:
            res = []
        _logger.info("res:"+str(res))
        return res


    #product_brand = fields.Many2one("product.brand",related='product_id.product_brand_id',string="Brand",store=True)
    product_main_cat = fields.Many2one("product.category",compute="_product_main_cat",store=True)
    product_main_cat_child = fields.Many2one("product.category",compute="_product_main_cat",store=True)
    #product_size = fields.Many2one("product.attribute.value",compute="_product_size_color",store=True)
    #product_color = fields.Many2one("product.attribute.value",compute="_product_size_color",store=True)

    #product_gender = fields.Many2one("product.attribute.value",compute="_product_size_color",store=True)

    product_company = fields.Many2one(related="product_id.company_id",string="Company",store=True,index=True)
    #product_shop = fields.Many2many(related="product_id.website_sale_shops",string="Shops",search='_search_shop')

class ProductecaConnectionBindingIntegration(models.Model):

    _name = "producteca.integration"
    _description = "Producteca Integration"
    _inherit = "ocapi.connection.binding"

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )

    integrationId = fields.Char(string="integrationId")
    app = fields.Char(string="app")


class OcapiConnectionBindingSaleOrderPayment(models.Model):

    _name = "producteca.payment"
    _description = "Producteca Sale Order Payment Binding"
    _inherit = "ocapi.binding.payment"

    order_id = fields.Many2one("producteca.sale_order",string="Order")
    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )
    name = fields.Char(string="Payment Name")

    date = fields.Datetime(string="date",index=True)
    amount = fields.Float(string="amount")
    couponAmount = fields.Float(string="couponAmount")
    status = fields.Char(string="status")
    method = fields.Char(string="method")
    integration_integrationId = fields.Char(string="integrationId")
    integration_app = fields.Char(string="app")
    transactionFee = fields.Float(string="transactionFee")
    installments = fields.Char(string="installments")
    card_paymentNetwork = fields.Char(string="card paymentNetwork")
    card_firstSixDigits = fields.Char(string="card firstSixDigits")
    card_lastFourDigits = fields.Char(string="card lastFourDigits")
    hasCancelableStatus = fields.Char(string="hasCancelableStatus")

    account_payment_id = fields.Many2one('account.payment',string='Pago')
    account_supplier_payment_id = fields.Many2one('account.payment',string='Pago a Proveedor')
    account_supplier_payment_shipment_id = fields.Many2one('account.payment',string='Pago Envio a Proveedor')

    def _get_ml_journal(self):
        journal_id = None
        #journal_id = self.env.user.company_id.mercadolibre_process_payments_journal
        #if not journal_id:
        #    journal_id = self.env['account.journal'].search([('code','=','ML')])
        #if not journal_id:
        #    journal_id = self.env['account.journal'].search([('code','=','MP')])
        return journal_id

    def _get_ml_partner(self):
        partner_id = None
        #partner_id = self.env.user.company_id.mercadolibre_process_payments_res_partner
        #if not partner_id:
        #    partner_id = self.env['res.partner'].search([('ref','=','MELI')])
        #if not partner_id:
        #    partner_id = self.env['res.partner'].search([('name','=','MercadoLibre')])
        return partner_id

    def _get_ml_customer_partner(self):
        sale_order = self._get_ml_customer_order()
        return (sale_order and sale_order.partner_id)

    def _get_ml_customer_order(self):
        mlorder = self.order_id
        mlshipment = mlorder.shipment
        return (mlorder and mlorder.sale_order) or (mlshipment and mlshipment.sale_order)

    def create_payment(self):
        self.ensure_one()
        if self.account_payment_id:
            raise ValidationError('Ya esta creado el pago')
        if self.status != 'approved':
            return None
        journal_id = self._get_ml_journal()
        payment_method_id = self.env['account.payment.method'].search([('code','=','electronic'),('payment_type','=','inbound')])
        if not journal_id or not payment_method_id:
            raise ValidationError('Debe configurar el diario/metodo de pago')
        partner_id = self._get_ml_customer_partner()
        currency_id = self.env['res.currency'].search([('name','=',self.currency_id)])
        if not currency_id:
            raise ValidationError('No se puede encontrar la moneda del pago')

        communication = self.payment_id
        if self._get_ml_customer_order():
            communication = ""+str(self._get_ml_customer_order().name)+" OP "+str(self.payment_id)+str(" TOT")

        vals_payment = {
                'partner_id': partner_id.id,
                'payment_type': 'inbound',
                'payment_method_id': payment_method_id.id,
                'journal_id': journal_id.id,
                'meli_payment_id': self.id,
                'communication': communication,
                'currency_id': currency_id.id,
                'partner_type': 'customer',
                'amount': self.total_paid_amount,
                }
        acct_payment_id = self.env['account.payment'].create(vals_payment)
        acct_payment_id.post()
        self.account_payment_id = acct_payment_id.id

    def create_supplier_payment(self):
        self.ensure_one()
        if self.status != 'approved':
            return None
        if self.account_supplier_payment_id:
            raise ValidationError('Ya esta creado el pago')
        journal_id = self._get_ml_journal()
        payment_method_id = self.env['account.payment.method'].search([('code','=','outbound_online'),('payment_type','=','outbound')])
        if not journal_id or not payment_method_id:
            raise ValidationError('Debe configurar el diario/metodo de pago')
        partner_id = self._get_ml_partner()
        if not partner_id:
            raise ValidationError('No esta dado de alta el proveedor MercadoLibre')
        currency_id = self.env['res.currency'].search([('name','=',self.currency_id)])
        if not currency_id:
            raise ValidationError('No se puede encontrar la moneda del pago')

        communication = self.payment_id
        if self._get_ml_customer_order():
            communication = ""+str(self._get_ml_customer_order().name)+" OP "+str(self.payment_id)+str(" FEE")

        vals_payment = {
                'partner_id': partner_id.id,
                'payment_type': 'outbound',
                'payment_method_id': payment_method_id.id,
                'journal_id': journal_id.id,
                'meli_payment_id': self.id,
                'communication': communication,
                'currency_id': currency_id.id,
                'partner_type': 'supplier',
                'amount': self.fee_amount,
                }
        acct_payment_id = self.env['account.payment'].create(vals_payment)
        acct_payment_id.post()
        self.account_supplier_payment_id = acct_payment_id.id

    def create_supplier_payment_shipment(self):
        self.ensure_one()
        if self.status != 'approved':
            return None
        if self.account_supplier_payment_shipment_id:
            raise ValidationError('Ya esta creado el pago')
        journal_id = self._get_ml_journal()
        payment_method_id = self.env['account.payment.method'].search([('code','=','outbound_online'),('payment_type','=','outbound')])
        if not journal_id or not payment_method_id:
            raise ValidationError('Debe configurar el diario/metodo de pago')
        partner_id = self._get_ml_partner()
        if not partner_id:
            raise ValidationError('No esta dado de alta el proveedor MercadoLibre')
        currency_id = self.env['res.currency'].search([('name','=',self.currency_id)])
        if not currency_id:
            raise ValidationError('No se puede encontrar la moneda del pago')
        if (not self.order_id or not self.order_id.shipping_list_cost>0.0):
            raise ValidationError('No hay datos de costo de envio')

        communication = self.payment_id
        if self._get_ml_customer_order():
            communication = ""+str(self._get_ml_customer_order().name)+" OP "+str(self.payment_id)+str(" SHP")

        vals_payment = {
                'partner_id': partner_id.id,
                'payment_type': 'outbound',
                'payment_method_id': payment_method_id.id,
                'journal_id': journal_id.id,
                'meli_payment_id': self.id,
                'communication': communication,
                'currency_id': currency_id.id,
                'partner_type': 'supplier',
                'amount': self.order_id.shipping_list_cost,
                }
        acct_payment_id = self.env['account.payment'].create(vals_payment)
        acct_payment_id.post()
        self.account_supplier_payment_shipment_id = acct_payment_id.id


class OcapiConnectionBindingSaleOrderShipmentItem(models.Model):

    _name = "producteca.shipment.item"
    _description = "Ocapi Sale Order Shipment Item"
    _inherit = "ocapi.binding.shipment.item"

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )
    shipping_id = fields.Many2one("producteca.shipment",string="Shipment")
    product = fields.Char(string="Product Id")
    variation = fields.Char(string="Variation Id")
    quantity = fields.Float(string="Quantity")


class OcapiConnectionBindingSaleOrderShipment(models.Model):

    _name = "producteca.shipment"
    _description = "Ocapi Sale Order Shipment Binding"
    _inherit = "ocapi.binding.shipment"

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )

    order_id = fields.Many2one("producteca.sale_order",string="Order")
    products = fields.One2many("producteca.shipment.item", "shipping_id", string="Product Items")

    date = fields.Datetime(string="date",index=True)
    method_trackingNumber = fields.Char(string="trackingNumber")
    method_trackingUrl = fields.Char(string="trackingUrl")
    method_labelUrl = fields.Char(string="labelUrl")
    method_courier = fields.Char(string="courier")
    method_mode = fields.Char(string="mode")
    method_cost = fields.Char(string="cost")
    method_eta = fields.Char(string="eta")
    method_status = fields.Char(string="status")
    integration_app = fields.Char(string="app")
    integration_integrationId = fields.Char(string="integrationId")
    integration_status = fields.Char(string="status")
    integration_id = fields.Char(string="id")
    receiver_fullName = fields.Char(string="receiver_fullName")
    receiver_phoneNumber = fields.Char(string="receiver_phoneNumber")


class ProductecaConnectionBindingSaleOrderClient(models.Model):

    _name = "producteca.client"
    _description = "Producteca Client Binding"
    _inherit = "ocapi.binding.client"

    def get_display_name(self):
        for client in self:
            client.display_name = str(client.contactPerson)+" ["+str(client.name)+"]"

    display_name = fields.Char(string="Display Name",store=False,compute=get_display_name)
    type = fields.Char(string="Client Type") #Customer, ...
    contactPerson = fields.Char(string="Contact Person")
    mail = fields.Char(string="Mail")
    phoneNumber = fields.Char(string="Phonenumber")
    taxId = fields.Char(string="Tax ID")
    location_streetName = fields.Char(string="Street Name")
    location_streetNumber = fields.Char(string="Street Number")
    location_addressNotes = fields.Char(string="Address Notes")
    location_state = fields.Char(string="State")
    location_stateId = fields.Char(string="State Id")
    location_city = fields.Char(string="City")
    location_neighborhood = fields.Char(string="NeighborHood")
    location_zipCode = fields.Char(string="zipCode")

    profile = fields.Text(string="Profile") # { "app": 2, "integrationId": 63807563 }
    profile_app = fields.Integer(string="Profile App")
    profile_integrationId = fields.Integer(string="Profile Integration Id")

    billingInfo = fields.Text(string="billingInfo")
    billingInfo_docType = fields.Char(string="Doc Type")
    billingInfo_docNumber = fields.Char(string="Doc Number")
    billingInfo_streetName = fields.Char(string="Street Name")
    billingInfo_streetNumber = fields.Char(string="Street Number")
    billingInfo_zipCode = fields.Char(string="zipCode")
    billingInfo_city = fields.Char(string="city")
    billingInfo_state = fields.Char(string="state")
    billingInfo_stateId = fields.Char(string="state id")
    billingInfo_neighborhood = fields.Char(string="neighborhood")
    billingInfo_businessName = fields.Char(string="businessName")
    billingInfo_stateRegistration = fields.Char(string="stateRegistration")
    billingInfo_taxPayerType = fields.Char(string="taxPayerType")
    billingInfo_firstName = fields.Char(string="firstName")
    billingInfo_lastName = fields.Char(string="lastName")

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )


class ProductecaConnectionBindingSaleOrderLine(models.Model):

    _name = "producteca.sale_order_line"
    _description = "Producteca Sale Order Line Binding"
    _inherit = "ocapi.binding.sale_order_line"

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )
    order_id = fields.Many2one("producteca.sale_order",string="Order")

    price = fields.Float(string="Price")
    originalPrice = fields.Float(string="originalPrice")
    quantity = fields.Float(string="Quantity")
    reserved = fields.Float(string="Reserved")
    conversation = fields.Text(string="Conversation")

    #product
    product_name = fields.Char(string="Product Name")
    product_code = fields.Char(string="Product Code")
    product_brand = fields.Char(string="Product Brand")
    product_id = fields.Char(string="Product Id")
    #variation
    variation_integrationId = fields.Char(string="integrationId")
    variation_maxAvailableStock = fields.Integer(string="maxAvailableStock")
    variation_minAvailableStock = fields.Integer(string="minAvailableStock")
    variation_primaryColor = fields.Char(string="primaryColor")
    variation_size = fields.Char(string="size")
    variation_id = fields.Char(string="Variation Id")
    variation_sku = fields.Char(string="Variation Sku")

    variation_stocks = fields.Text(string="Stocks")
    variation_pictures = fields.Text(string="Pictures")
    variation_attributes = fields.Text(string="Attributes")
    #variation_stocks_warehouse = fields.Char(string="Warehouse")
    #variation_stocks_warehouse = fields.Char(string="Warehouse")

class ProductecaConnectionBindingSaleOrder(models.Model):

    _name = "producteca.sale_order"
    _description = "Producteca Sale Order Binding Sale"
    _inherit = "ocapi.binding.sale_order"

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )
    client = fields.Many2one("producteca.client",string="Client",index=True)

    lines = fields.One2many("producteca.sale_order_line","order_id", string="Order Items")
    payments = fields.One2many("producteca.payment","order_id",string="Order Payments")
    shipments = fields.One2many("producteca.shipment","order_id",string="Order Shipments")

    #id connector_id

    channel = fields.Char(string="Channel",index=True)
    channel_id = fields.Many2one( "producteca.channel", string="Channel Object")
    tags = fields.Char(string="Tags",index=True)
    integrations = fields.Text(string="Integrations",index=True)
    integrations_integrationId = fields.Char(string="integrationId",index=True)
    integrations_app = fields.Char(string="app",index=True)
    integrations_alternateId = fields.Char(string="alternateId")
    cartId = fields.Char(string="cartId",help="Id de carrito (pack_id)")
    warehouse = fields.Text(string="Warehouse",index=True)
    warehouseIntegration = fields.Text(string="WarehouseIntegration",index=True)

    amount = fields.Float(string="Amount",index=True)
    shippingCost = fields.Float(string="Shipping Cost",index=True)
    financialCost = fields.Float(string="Financial Cost",index=True)
    paidApproved = fields.Float(string="Paid Approved",index=True)

    paymentStatus = fields.Char(string="paymentStatus",index=True)
    deliveryStatus = fields.Char(string="deliveryStatus",index=True)
    paymentFulfillmentStatus = fields.Char(string="paymentFulfillmentStatus",index=True)

    deliveryFulfillmentStatus = fields.Char(string="deliveryFulfillmentStatus",index=True)
    deliveryMethod = fields.Char(string="deliveryMethod",index=True)
    logisticType = fields.Char(string="logisticType",index=True)
    paymentTerm = fields.Char(string="paymentTerm",index=True)
    currency = fields.Char(string="currency",index=True)
    customId = fields.Char(string="customId",index=True)

    isOpen = fields.Boolean(string="isOpen",index=True)
    isCanceled = fields.Boolean(string="isCanceled",index=True)
    hasAnyShipments = fields.Boolean(string="hasAnyShipments",index=True)

    date = fields.Datetime(string="date",index=True)
    mail = fields.Char(string="Mail")

    def update(self):
        _logger.info("Update producteca order")
        #check from last notification

class ProductecaConnectionBindingProductCategory(models.Model):

    _name = "producteca.category"
    _description = "Producteca Binding Category"
    _inherit = "ocapi.binding.category"

    connection_account = fields.Many2one( "producteca.account", string="Producteca Account" )

    name = fields.Char(string="Category",index=True)
    category_id = fields.Char(string="Category Id",index=True)
