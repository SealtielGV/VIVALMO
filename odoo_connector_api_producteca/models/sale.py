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

class SaleOrder(models.Model):

    _inherit = "sale.order"

    #mercadolibre could have more than one associated order... packs are usually more than one order
    producteca_bindings = fields.Many2many( "producteca.sale_order", string="Producteca Connection Bindings" )
    
    def producteca_update( self, context=None ):
        _logger.info("producteca_update:"+str(self))
        context = context or self.env.context
        for so in self:
            if so.producteca_bindings:
                pso = so.producteca_bindings[0]                
                if pso:
                    ret = pso.update()
                    if ret and 'name' in ret:
                        _logger.error(ret)
                        return ret
                        
    def producteca_deliver( self ):
        _logger.info("producteca_deliver")
        res= {}
        if self.picking_ids:
            for spick in self.picking_ids:
                _logger.info(spick)
                if (spick.move_line_ids):
                    _logger.info(spick.move_line_ids)
                    if (len(spick.move_line_ids)>=1):
                        for pop in spick.move_line_ids:
                            _logger.info(pop)
                            if (pop.qty_done==0.0 and pop.product_qty>=0.0):
                                pop.qty_done = pop.product_qty
                        _logger.info("producteca_deliver > validating")
                        try:
                            spick.button_validate()
                            spick.action_done()
                            continue;
                        except Exception as e:
                            _logger.error("producteca_deliver > stock pick button_validate/action_done error"+str(e))
                            res = { 'error': str(e) }
                            pass;

                        try:
                            spick.action_assign()
                            spick.button_validate()
                            spick.action_done()
                            continue;
                        except Exception as e:
                            _logger.error("stock pick action_assign/button_validate/action_done error"+str(e))
                            res = { 'error': str(e) }
                            pass;
        return res

class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    #here we must use Many2one more accurate, there is no reason to have more than one binding (more than one account and more than one item/order associated to one sale order line)
    producteca_bindings = fields.Many2one( "producteca.sale_order_line", string="Producteca Connection Bindings" )

class ResPartner(models.Model):

    _inherit = "res.partner"
    
    #several possible relations? we really dont know for sure, how to not duplicate clients from different platforms
    #besides, is there a way to identify duplicates other than integration ids
    producteca_bindings = fields.Many2many( "producteca.client", string="Producteca Connection Bindings" )

            
            
