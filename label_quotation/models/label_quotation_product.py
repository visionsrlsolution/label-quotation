# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LabelQuotationProduct(models.Model):
    _name = 'label.quotation.product'
    _description = 'Label Quotation with Product Integration'
    _inherit = ['label.quotation']
    
    # Product-based fields
    material_product_id = fields.Many2one(
        'product.template',
        string='Material Product',
        domain=[('is_label_material', '=', True)],
        help='Material product from Odoo product catalog'
    )
    
    machine_product_id = fields.Many2one(
        'product.template',
        string='Machine Product',
        domain=[('is_label_machine', '=', True)],
        help='Machine product from Odoo product catalog'
    )
    
    die_product_id = fields.Many2one(
        'product.template',
        string='Die Product',
        domain=[('is_label_die', '=', True)],
        help='Die product from Odoo product catalog'
    )
    
    # Computed fields for compatibility
    @api.depends('material_product_id')
    def _compute_material_data(self):
        """Compute material data from product"""
        for record in self:
            if record.material_product_id and record.material_product_id.is_label_material:
                record.material_data = record.material_product_id.get_material_data()
            else:
                record.material_data = {}
    
    material_data = fields.Json(
        string='Material Data',
        compute='_compute_material_data',
        help='Material data extracted from product'
    )
    
    @api.depends('machine_product_id')
    def _compute_machine_data(self):
        """Compute machine data from product"""
        for record in self:
            if record.machine_product_id and record.machine_product_id.is_label_machine:
                record.machine_data = record.machine_product_id.get_machine_data()
            else:
                record.machine_data = {}
    
    machine_data = fields.Json(
        string='Machine Data',
        compute='_compute_machine_data',
        help='Machine data extracted from product'
    )
    
    @api.depends('die_product_id')
    def _compute_die_data(self):
        """Compute die data from product"""
        for record in self:
            if record.die_product_id and record.die_product_id.is_label_die:
                record.die_data = record.die_product_id.get_die_data()
            else:
                record.die_data = {}
    
    die_data = fields.Json(
        string='Die Data',
        compute='_compute_die_data',
        help='Die data extracted from product'
    )
    
    # Override methods to use product data
    @api.depends('material_product_id', 'label_width', 'label_height', 'tracks', 'interspace')
    def _compute_web_width(self):
        """Compute web width using product data"""
        for record in self:
            if record.material_product_id and record.material_product_id.is_label_material:
                material_data = record.material_product_id.get_material_data()
                max_width = material_data.get('max_width', 0)
                
                if record.tracks and record.label_width and record.interspace:
                    calculated_width = (record.tracks * record.label_width) + ((record.tracks - 1) * record.interspace)
                    record.web_width = min(calculated_width, max_width) if max_width > 0 else calculated_width
                else:
                    record.web_width = 0
            else:
                record.web_width = 0
    
    @api.depends('machine_product_id', 'web_width', 'total_quantity')
    def _compute_production_time(self):
        """Compute production time using product data"""
        for record in self:
            if record.machine_product_id and record.machine_product_id.is_label_machine:
                machine_data = record.machine_product_id.get_machine_data()
                max_speed = machine_data.get('max_speed', 0)
                efficiency = machine_data.get('efficiency_factor', 1.0)
                
                if max_speed > 0 and record.web_width > 0 and record.total_quantity > 0:
                    # Calculate production time in minutes
                    labels_per_meter = 1000 / (record.label_height + record.interspace) if record.label_height > 0 else 0
                    meters_needed = record.total_quantity / (labels_per_meter * record.tracks) if labels_per_meter > 0 and record.tracks > 0 else 0
                    production_time = (meters_needed / max_speed) / efficiency
                    record.production_time = production_time
                else:
                    record.production_time = 0
            else:
                record.production_time = 0
    
    @api.depends('material_product_id', 'web_width', 'production_time')
    def _compute_material_cost(self):
        """Compute material cost using product data"""
        for record in self:
            if record.material_product_id and record.material_product_id.is_label_material:
                material_data = record.material_product_id.get_material_data()
                cost_per_sqm = material_data.get('cost_per_sqm', 0)
                waste_factor = material_data.get('waste_factor', 0)
                
                if cost_per_sqm > 0 and record.web_width > 0 and record.production_time > 0:
                    # Calculate material area in square meters
                    web_width_m = record.web_width / 1000
                    production_length_m = record.production_time * 60  # Convert to meters (assuming 1 m/min average)
                    material_area = web_width_m * production_length_m
                    
                    # Apply waste factor
                    total_material_area = material_area * (1 + waste_factor / 100)
                    record.material_cost = total_material_area * cost_per_sqm
                else:
                    record.material_cost = 0
            else:
                record.material_cost = 0
    
    @api.depends('machine_product_id', 'production_time')
    def _compute_machine_cost(self):
        """Compute machine cost using product data"""
        for record in self:
            if record.machine_product_id and record.machine_product_id.is_label_machine:
                machine_data = record.machine_product_id.get_machine_data()
                production_cost_per_hour = machine_data.get('production_cost_per_hour', 0)
                setup_cost_per_hour = machine_data.get('setup_cost_per_hour', 0)
                setup_time = machine_data.get('setup_time', 0)
                
                if production_cost_per_hour > 0 and record.production_time > 0:
                    # Calculate costs
                    production_cost = (record.production_time / 60) * production_cost_per_hour
                    setup_cost = (setup_time / 60) * setup_cost_per_hour if setup_time > 0 else 0
                    record.machine_cost = production_cost + setup_cost
                else:
                    record.machine_cost = 0
            else:
                record.machine_cost = 0
    
    @api.depends('die_product_id', 'total_quantity')
    def _compute_die_cost(self):
        """Compute die cost using product data"""
        for record in self:
            if record.die_product_id and record.die_product_id.is_label_die:
                die_data = record.die_product_id.get_die_data()
                cost_per_use = die_data.get('cost_per_use', 0)
                depreciation_per_use = die_data.get('depreciation_per_use', 0)
                
                if cost_per_use > 0 and record.total_quantity > 0:
                    # Calculate die cost based on usage
                    total_die_cost = cost_per_use + depreciation_per_use
                    record.die_cost = total_die_cost
                else:
                    record.die_cost = 0
            else:
                record.die_cost = 0
    
    # Override total cost calculation
    @api.depends('material_cost', 'machine_cost', 'die_cost', 'labor_cost', 'overhead_cost')
    def _compute_total_cost(self):
        """Compute total cost using product-based calculations"""
        for record in self:
            record.total_cost = (
                record.material_cost +
                record.machine_cost +
                record.die_cost +
                record.labor_cost +
                record.overhead_cost
            )
    
    # Methods for product integration
    def action_create_sale_order(self):
        """Create sale order with products"""
        self.ensure_one()
        
        if not self.material_product_id or not self.machine_product_id or not self.die_product_id:
            raise ValidationError(_('Please select material, machine, and die products before creating sale order.'))
        
        # Create sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'date_order': fields.Date.context_today(self),
            'company_id': self.company_id.id,
        })
        
        # Add material product line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.material_product_id.id,
            'product_uom_qty': self.total_quantity,
            'price_unit': self.material_product_id.list_price,
        })
        
        # Add machine service line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.machine_product_id.id,
            'product_uom_qty': self.production_time / 60,  # Convert to hours
            'price_unit': self.machine_product_id.list_price,
        })
        
        # Add die service line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.die_product_id.id,
            'product_uom_qty': 1,  # One die setup
            'price_unit': self.die_product_id.list_price,
        })
        
        # Update quotation state
        self.state = 'accepted'
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_generate_pdf(self):
        """Generate PDF quotation with product details"""
        self.ensure_one()
        
        # This would integrate with a PDF report that includes product information
        return {
            'type': 'ir.actions.report',
            'report_name': 'label_quotation.quotation_report',
            'report_type': 'qweb-pdf',
            'data': {'ids': [self.id]},
            'context': {'active_ids': [self.id]},
        }
