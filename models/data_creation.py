# -*- coding: utf-8 -*-

from odoo import models, api, _


class DataCreation(models.Model):
    _name = 'data.creation'
    _description = 'Data Creation Helper'

    @api.model
    def create_label_data(self):
        """Create all label quotation data programmatically"""
        
        # Create product categories
        self._create_product_categories()
        
        # Create products
        self._create_products()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Label quotation data created successfully!'),
                'type': 'success',
            }
        }
    
    def _create_product_categories(self):
        """Create product categories"""
        
        # Get main category
        main_category = self.env.ref('product.product_category_all', raise_if_not_found=False)
        if not main_category:
            return
        
        # Create categories if they don't exist
        categories_data = [
            {
                'name': 'Label Materials',
                'parent_id': main_category.id,
            },
            {
                'name': 'Label Machines', 
                'parent_id': main_category.id,
            },
            {
                'name': 'Label Dies',
                'parent_id': main_category.id,
            },
            {
                'name': 'Label Services',
                'parent_id': main_category.id,
            }
        ]
        
        for cat_data in categories_data:
            existing = self.env['product.category'].search([
                ('name', '=', cat_data['name'])
            ], limit=1)
            
            if not existing:
                self.env['product.category'].create(cat_data)
    
    def _create_products(self):
        """Create products"""
        
        # Get categories
        materials_cat = self.env['product.category'].search([
            ('name', '=', 'Label Materials')
        ], limit=1)
        
        machines_cat = self.env['product.category'].search([
            ('name', '=', 'Label Machines')
        ], limit=1)
        
        dies_cat = self.env['product.category'].search([
            ('name', '=', 'Label Dies')
        ], limit=1)
        
        if not all([materials_cat, machines_cat, dies_cat]):
            return
        
        # Create materials
        materials_data = [
            {
                'name': 'Thermal FSC',
                'default_code': 'CATEA02',
                'categ_id': materials_cat.id,
                'type': 'product',
                'sale_ok': True,
                'purchase_ok': True,
                'list_price': 0.85,
                'standard_price': 0.65,
                'is_label_material': True,
                'paper_type': 'thermal',
                'grammage': 146,
                'thickness': 122,
                'adhesive_type': 'hot_melt',
                'adhesive_strength': 'standard',
                'max_width': 425,
                'max_length': 4000,
                'waste_factor': 4.0,
                'description': 'FSC certified thermal paper with hot melt adhesive',
            },
            {
                'name': 'Vellum Neutro FSC',
                'default_code': 'CAVA03',
                'categ_id': materials_cat.id,
                'type': 'product',
                'sale_ok': True,
                'purchase_ok': True,
                'list_price': 0.65,
                'standard_price': 0.45,
                'is_label_material': True,
                'paper_type': 'vellum',
                'grammage': 136,
                'thickness': 125,
                'adhesive_type': 'hot_melt',
                'adhesive_strength': 'standard',
                'max_width': 325,
                'max_length': 4000,
                'waste_factor': 5.0,
                'description': 'FSC certified vellum paper with hot melt adhesive',
            }
        ]
        
        # Create machines
        machines_data = [
            {
                'name': 'Prati Vega Plus LF450',
                'default_code': 'VEGA_LF450',
                'categ_id': machines_cat.id,
                'type': 'service',
                'sale_ok': True,
                'purchase_ok': False,
                'list_price': 80.00,
                'standard_price': 60.00,
                'is_label_machine': True,
                'machine_type': 'vega_plus',
                'manufacturer': 'Prati',
                'model': 'LF450',
                'max_speed': 300,
                'min_speed': 20,
                'max_web_width': 400,
                'min_web_width': 50,
                'setup_time': 30,
                'max_tracks': 6,
                'precision_rating': 'high',
                'quality_factor': 1.2,
                'description': 'High-speed die-cutting machine for labels up to 400mm width',
            }
        ]
        
        # Create dies
        dies_data = [
            {
                'name': 'Rectangle 50x30mm',
                'default_code': 'RECT_50_30',
                'categ_id': dies_cat.id,
                'type': 'service',
                'sale_ok': True,
                'purchase_ok': True,
                'list_price': 0.50,
                'standard_price': 0.35,
                'is_label_die': True,
                'die_type': 'rotary',
                'die_width': 50,
                'die_length': 30,
                'repeat_length': 32,
                'die_max_tracks': 8,
                'cutting_force_required': 2.5,
                'stripping_difficulty': 'easy',
                'expected_lifetime_cuts': 100000,
                'current_usage_count': 0,
                'cost_per_use': 0.50,
                'description': 'Standard rectangular die for small labels',
            }
        ]
        
        # Create all products
        all_products = materials_data + machines_data + dies_data
        
        for product_data in all_products:
            existing = self.env['product.template'].search([
                ('default_code', '=', product_data['default_code'])
            ], limit=1)
            
            if not existing:
                self.env['product.template'].create(product_data)
