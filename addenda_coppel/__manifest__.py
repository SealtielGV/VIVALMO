# -*- coding: utf-8 -*-
{
    'name': "Addenda Coppel",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "GBM, Soluciones 4G",
    'website': "https://www.soluciones4g.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': 
    [
        'account',
        'product',
        'sale',
        'stock'
    ],
    'data' : [
        'views/addenda_coppel.xml',
        'views/addenda_fields.xml'
    ],
    'installable':True,
    'auto_install':False,    
}