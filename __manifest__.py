# -*- coding: utf-8 -*-
{
    'name': 'label-quotation',
    'version': '19.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Label quotation system with product integration',
    'description': 'Advanced label quotation system with production optimization',
    'author': 'Your Company',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/product_categories.xml',
        'data/label_products.xml',
        'views/label_product_views.xml',
        'views/label_quotation_main_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}