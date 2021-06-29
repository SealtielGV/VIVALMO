# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo import api, models, fields
import logging

_logger = logging.getLogger(__name__)

class ProductTemplateBindToProducteca(models.TransientModel):

    _name = "producteca.binder.wiz"
    _description = "Wizard de Product Template Producteca Binder"
    _inherit = "ocapi.binder.wiz"

    connectors = fields.Many2many("producteca.account", string='Producteca Accounts')

    def product_template_add_to_connector(self, context=False):

        _logger.info("product_template_add_to_connector (Producteca)")

        company = self.env.user.company_id
        context = context or self.env.context
        product_ids = context['active_ids']
        product_obj = self.env['product.template']

        res = {}
        for product_id in product_ids:
            
            product = product_obj.browse(product_id)
                        
            for producteca in self.connectors:
                _logger.info(_("Check %s in %s") % (product.display_name, producteca.name))
                #Binding to
                product.producteca_bind_to( producteca )                                 
                        
                
    def product_template_remove_from_connector(self, context=False):

        _logger.info("product_template_remove_from_connector (Producteca)")

        company = self.env.user.company_id
        context = context or self.env.context
        product_ids = context['active_ids']
        product_obj = self.env['product.template']

        res = {}
        for product_id in product_ids:
            
            product = product_obj.browse(product_id)
                        
            for producteca in self.connectors:
                _logger.info(_("Check %s in %s") % (product.display_name, producteca.name))
                #Binding to
                product.producteca_unbind_from( producteca )       
                
                
                
class ProductProductBindToProducteca(models.TransientModel):

    _name = "producteca.variant.binder.wiz"
    _description = "Wizard de Product Variant Producteca Binder"
    _inherit = "ocapi.binder.wiz"

    connectors = fields.Many2many("producteca.account", string='Producteca Accounts')

    def product_product_add_to_connector(self, context=False):

        _logger.info("product_product_add_to_connector (Producteca)")

        company = self.env.user.company_id
        context = context or self.env.context
        product_ids = context['active_ids']
        product_obj = self.env['product.product']

        res = {}
        for product_id in product_ids:
            
            product = product_obj.browse(product_id)
                        
            for producteca in self.connectors:
                _logger.info(_("Check %s in %s") % (product.display_name, producteca.name))
                #Binding to
                product.producteca_bind_to( producteca )                                 
                        
                
    def product_product_remove_from_connector(self, context=False):

        _logger.info("product_product_remove_from_connector (Producteca)")

        company = self.env.user.company_id
        context = context or self.env.context
        product_ids = context['active_ids']
        product_obj = self.env['product.product']

        res = {}
        for product_id in product_ids:
            
            product = product_obj.browse(product_id)
                        
            for producteca in self.connectors:
                _logger.info(_("Check %s in %s") % (product.display_name, producteca.name))
                #Binding to
                product.producteca_unbind_from( producteca )       