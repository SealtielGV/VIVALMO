# -*- coding: utf-8 -*-
{
    'name': "Cantidad Campos",

    'summary': """Cantidad Campos""",

    'description': """Cantidad Campos""",

    'author': "Estrasol - Arturo",
    'website': "",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','account','purchase','sale','stock'],
    'data' : [
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml'
    ],
    'installable':True,
    'auto_install':False,    
    'application': True,
}