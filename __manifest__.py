# -*- coding: utf-8 -*-
{
    'name': 'Label Quotation System',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Quotation system for blank label production with die-cutting calculations',
    'description': """
        Label Quotation System
        =====================
        
        This module provides a comprehensive quotation system for blank label production
        including die-cutting calculations, material costs, and machine overhead.
        
        Features:
        - Paper material management (types, grammage, costs)
        - Die management with dimensions and costs
        - Machine management with overhead calculations
        - Label quotation with automatic calculations
        - Integration with Odoo sales orders
        - Support for Vega+ and Digicompact machines
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base', 'sale', 'stock', 'mrp', 'mail'],
    'external_dependencies': {
        'python': ['reportlab'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequences.xml',
        'data/paper_types.xml',
        'data/machine_types.xml',
        'views/carta_views.xml',
        'views/fustella_views.xml',
        'views/macchina_views.xml',
        'views/label_quotation_views.xml',
        'views/label_config_views.xml',
        'views/sale_order_views.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
