# -*- coding: utf-8 -*-

import re
from odoo import models, fields, api, _
from odoo.tools.misc import ustr
from odoo.exceptions import ValidationError

class AddendaCompany(models.Model):
	"""docstring for AddendaCompany"""
	_inherit = 'res.company'

	x_supplier_id = fields.Char(string='Identificador Proveedor')
	x_supplier_type = fields.Char(string='Tipo de proveedor',default='2')

class AddendaProduct(models.Model):
	_inherit = 'product.template'
	
	x_code = fields.Char(string='Código',compute="_compute_x_code",inverse="_set_x_code", store=True)
	x_size = fields.Char(string='Talla',compute="_compute_x_size",inverse="_set_x_size", store=True)
	x_model = fields.Char(string='Modelo',compute="_compute_x_model",inverse="_set_x_model", store=True)

	@api.depends('product_variant_ids.x_code')
	def _compute_x_code(self):
		unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
		for template in unique_variants:
			template.x_code = template.product_variant_ids.x_code
		for template in (self - unique_variants):
			template.x_code = False

	def _set_x_code(self):
		if len(self.product_variant_ids) == 1:
			self.product_variant_ids.x_code = self.x_code

	@api.depends('product_variant_ids.x_size')
	def _compute_x_size(self):
		unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
		for template in unique_variants:
			template.x_size = template.product_variant_ids.x_size
		for template in (self - unique_variants):
			template.x_size = False

	def _set_x_size(self):
		if len(self.product_variant_ids) == 1:
			self.product_variant_ids.x_size = self.x_size

	@api.depends('product_variant_ids.x_model')
	def _compute_x_model(self):
		unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
		for template in unique_variants:
			template.x_model = template.product_variant_ids.x_model
		for template in (self - unique_variants):
			template.x_model = False

	def _set_x_model(self):
		if len(self.product_variant_ids) == 1:
			self.product_variant_ids.x_model = self.x_model


class AddendaProduct(models.Model):
	_inherit = 'product.product'
	
	x_code = fields.Char(string='Código de artículo Coppel', index=True)
	x_size = fields.Char(string='Talla de artículo Coppel', index=True)
	x_model = fields.Char(string='Modelo Coppel', index=True)

class AddendaSale(models.Model):
	"""docstring for AddendaFields"""
	_inherit = 'sale.order'

	x_order_no = fields.Char(string='Número de pedido Coppel')
	x_warehouse_code = fields.Char(string='Número de bodega Coppel')
	x_name_warehouse = fields.Char(string='Nombre de bodega Coppel')
	x_street_warehouse = fields.Char(string='Calle de bodega Coppel')

class AddendaPicking(models.Model):
	_inherit = 'stock.picking'
	
	x_qty_lote = fields.Integer(string='Total de lotes o cajas [Coppel]')

class AddendaOrderLine(models.Model):
	_inherit = 'sale.order.line'
	
	x_qty = fields.Float(string='Piezas por caja [Coppel]')
	x_quantity = fields.Float(string='Total de piezas por talla [Coppel]')

	def _amount_with_discount(self):
		with_discount = 0.0
		for line in self:
			with_discount += line.price_unit * (1 - (line.discount or 0.0) / 100.0)
		return with_discount

	def _compute_amount_discounted(self):
		total = 0.0
		for line in self:
			total += total + line.price_unit * (1 - (line.discount or 0.0) / 100.0)
		return total