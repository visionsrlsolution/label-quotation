# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Label-specific fields
    is_label_material = fields.Boolean(
        string='Is Label Material',
        help='Check if this product is a label material'
    )
    
    is_label_machine = fields.Boolean(
        string='Is Label Machine',
        help='Check if this product is a label production machine'
    )
    
    is_label_die = fields.Boolean(
        string='Is Label Die',
        help='Check if this product is a label die cutting tool'
    )
    
    # Material-specific fields (when is_label_material = True)
    paper_type = fields.Selection([
        ('thermal', 'Thermal'),
        ('vellum', 'Vellum'),
        ('adhesive', 'Adhesive'),
        ('plain', 'Plain'),
        ('coated', 'Coated'),
        ('recycled', 'Recycled'),
    ], string='Paper Type')
    
    grammage = fields.Float(
        string='Grammage (g/m²)',
        help='Weight per square meter in grams'
    )
    
    thickness = fields.Float(
        string='Thickness (mm)',
        help='Thickness of the paper in millimeters'
    )
    
    adhesive_type = fields.Selection([
        ('hot_melt', 'Hot Melt'),
        ('permanent', 'Permanent'),
        ('removable', 'Removable'),
        ('repositionable', 'Repositionable'),
        ('none', 'None'),
    ], string='Adhesive Type', default='none')
    
    adhesive_strength = fields.Selection([
        ('low', 'Low'),
        ('standard', 'Standard'),
        ('strong', 'Strong'),
        ('high', 'High'),
    ], string='Adhesive Strength')
    
    max_width = fields.Float(
        string='Max Width (mm)',
        help='Maximum width available for this material'
    )
    
    max_length = fields.Float(
        string='Max Length (mm)',
        help='Maximum length available for this material'
    )
    
    waste_factor = fields.Float(
        string='Waste Factor (%)',
        default=5.0,
        help='Percentage of material waste during production'
    )
    
    minimum_order_quantity = fields.Float(
        string='Minimum Order Quantity (m)',
        help='Minimum linear meters that must be ordered'
    )
    
    roll_width_standard = fields.Float(
        string='Standard Roll Width (mm)',
        help='Standard width of material rolls'
    )
    
    roll_length_standard = fields.Float(
        string='Standard Roll Length (m)',
        help='Standard length of material rolls'
    )
    
    liner_type = fields.Selection([
        ('glassine', 'Glassine'),
        ('pet', 'PET'),
        ('pe', 'PE'),
        ('paper', 'Paper'),
        ('none', 'None'),
    ], string='Liner Type', default='glassine')
    
    liner_thickness = fields.Float(
        string='Liner Thickness (μm)',
        help='Thickness of liner in micrometers'
    )
    
    print_compatibility = fields.Selection([
        ('thermal_transfer', 'Thermal Transfer'),
        ('direct_thermal', 'Direct Thermal'),
        ('inkjet', 'Inkjet'),
        ('laser', 'Laser'),
        ('flexographic', 'Flexographic'),
        ('offset', 'Offset'),
    ], string='Print Compatibility')
    
    temperature_range_min = fields.Float(
        string='Min Temperature (°C)',
        help='Minimum operating temperature'
    )
    
    temperature_range_max = fields.Float(
        string='Max Temperature (°C)',
        help='Maximum operating temperature'
    )
    
    shelf_life_months = fields.Integer(
        string='Shelf Life (Months)',
        help='Material shelf life in months'
    )
    
    # Machine-specific fields (when is_label_machine = True)
    machine_type = fields.Selection([
        ('vega_plus', 'Vega Plus'),
        ('digicompact', 'Digicompact'),
        ('flexo', 'Flexographic'),
        ('offset', 'Offset'),
        ('digital', 'Digital'),
        ('screen', 'Screen Printing'),
        ('gravure', 'Gravure'),
    ], string='Machine Type')
    
    max_web_width = fields.Float(
        string='Max Web Width (mm)',
        help='Maximum web width the machine can handle'
    )
    
    max_speed = fields.Float(
        string='Max Speed (m/min)',
        help='Maximum production speed in meters per minute'
    )
    
    min_web_width = fields.Float(
        string='Min Web Width (mm)',
        help='Minimum web width the machine can handle'
    )
    
    min_speed = fields.Float(
        string='Min Speed (m/min)',
        help='Minimum production speed in meters per minute'
    )
    
    setup_time = fields.Float(
        string='Setup Time (minutes)',
        help='Time required to setup the machine in minutes'
    )
    
    die_change_time = fields.Float(
        string='Die Change Time (minutes)',
        help='Time required to change dies in minutes'
    )
    
    material_change_time = fields.Float(
        string='Material Change Time (minutes)',
        help='Time required to change materials in minutes'
    )
    
    warm_up_time = fields.Float(
        string='Warm-up Time (minutes)',
        help='Time required for machine warm-up in minutes'
    )
    
    max_tracks = fields.Integer(
        string='Maximum Tracks',
        help='Maximum number of tracks the machine can handle'
    )
    
    precision_rating = fields.Selection([
        ('low', 'Low (±0.5mm)'),
        ('standard', 'Standard (±0.2mm)'),
        ('high', 'High (±0.1mm)'),
        ('ultra', 'Ultra (±0.05mm)'),
    ], string='Precision Rating', default='standard')
    
    quality_factor = fields.Float(
        string='Quality Factor',
        default=1.0,
        help='Quality multiplier factor (affects pricing)'
    )
    
    setup_cost_per_hour = fields.Float(
        string='Setup Cost per Hour (€)',
        help='Cost per hour for machine setup'
    )
    
    production_cost_per_hour = fields.Float(
        string='Production Cost per Hour (€)',
        help='Cost per hour for production'
    )
    
    overhead_percentage = fields.Float(
        string='Overhead Percentage (%)',
        help='Overhead percentage applied to costs'
    )
    
    efficiency_factor = fields.Float(
        string='Efficiency Factor',
        help='Machine efficiency factor (0.0 to 1.0)'
    )
    
    maintenance_cost_per_month = fields.Float(
        string='Maintenance Cost per Month (€)',
        help='Monthly maintenance cost'
    )
    
    depreciation_cost_per_month = fields.Float(
        string='Depreciation Cost per Month (€)',
        help='Monthly depreciation cost'
    )
    
    energy_cost_per_hour = fields.Float(
        string='Energy Cost per Hour (€)',
        help='Energy cost per hour of operation'
    )
    
    operator_cost_per_hour = fields.Float(
        string='Operator Cost per Hour (€)',
        help='Operator cost per hour'
    )
    
    manufacturer = fields.Char(
        string='Manufacturer',
        help='Machine manufacturer'
    )
    
    model = fields.Char(
        string='Model',
        help='Machine model'
    )
    
    location = fields.Char(
        string='Location',
        help='Physical location of the machine'
    )
    
    # Die-specific fields (when is_label_die = True)
    die_type = fields.Selection([
        ('flatbed', 'Flatbed'),
        ('rotary', 'Rotary'),
        ('laser', 'Laser'),
        ('kiss_cut', 'Kiss Cut'),
    ], string='Die Type')
    
    die_width = fields.Float(
        string='Width (mm)',
        help='Width of the die in millimeters'
    )
    
    die_length = fields.Float(
        string='Length (mm)',
        help='Length of the die in millimeters'
    )
    
    repeat_length = fields.Float(
        string='Repeat Length (mm)',
        help='Length of one die repeat in millimeters'
    )
    
    die_max_tracks = fields.Integer(
        string='Maximum Tracks',
        help='Maximum number of tracks this die can handle'
    )
    
    cutting_force_required = fields.Float(
        string='Cutting Force Required (kN)',
        help='Force required for die cutting in kilonewtons'
    )
    
    stripping_difficulty = fields.Selection([
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('difficult', 'Difficult'),
        ('very_difficult', 'Very Difficult'),
    ], string='Stripping Difficulty', default='medium')
    
    expected_lifetime_cuts = fields.Integer(
        string='Expected Lifetime (cuts)',
        help='Expected number of cuts before die replacement'
    )
    
    current_usage_count = fields.Integer(
        string='Current Usage Count',
        help='Number of times this die has been used',
        default=0
    )
    
    cost_per_use = fields.Float(
        string='Cost per Use (€)',
        help='Cost per use of the die'
    )
    
    setup_time_die = fields.Float(
        string='Setup Time (hours)',
        help='Time required to setup the die'
    )
    
    # Computed fields
    @api.depends('expected_lifetime_cuts', 'cost_per_use')
    def _compute_depreciation_per_use(self):
        """Compute depreciation cost per use"""
        for record in self:
            if record.expected_lifetime_cuts > 0:
                # Assume initial cost is 100 times the cost per use (rough estimation)
                estimated_initial_cost = record.cost_per_use * 100
                record.depreciation_per_use = estimated_initial_cost / record.expected_lifetime_cuts
            else:
                record.depreciation_per_use = 0.0
    
    depreciation_per_use = fields.Float(
        string='Depreciation per Use (€)',
        compute='_compute_depreciation_per_use',
        help='Depreciation cost per use based on lifetime'
    )
    
    # Computed fields for legacy compatibility
    @api.depends('production_cost_per_hour', 'energy_cost_per_hour', 'operator_cost_per_hour', 'overhead_percentage')
    def _compute_hourly_cost(self):
        """Compute total hourly cost including overhead"""
        for record in self:
            base_cost = (record.production_cost_per_hour or 0) + (record.energy_cost_per_hour or 0) + (record.operator_cost_per_hour or 0)
            overhead = base_cost * (record.overhead_percentage or 0) / 100
            record.hourly_cost = base_cost + overhead
    
    hourly_cost = fields.Float(
        string='Hourly Cost (€)',
        compute='_compute_hourly_cost',
        help='Total hourly cost including overhead'
    )
    
    @api.depends('setup_cost_per_hour', 'setup_time')
    def _compute_setup_cost(self):
        """Compute total setup cost based on time and hourly rate"""
        for record in self:
            if record.setup_time and record.setup_cost_per_hour:
                record.setup_cost = (record.setup_time / 60) * record.setup_cost_per_hour
            else:
                record.setup_cost = 0
    
    setup_cost = fields.Float(
        string='Setup Cost (€)',
        compute='_compute_setup_cost',
        help='Total setup cost based on time and hourly rate'
    )
    
    # Constraints
    @api.constrains('is_label_material', 'is_label_machine', 'is_label_die')
    def _check_label_type(self):
        """Ensure only one label type is selected"""
        for record in self:
            types = [record.is_label_material, record.is_label_machine, record.is_label_die]
            if sum(types) > 1:
                raise ValidationError(_('A product can only be one type: material, machine, or die.'))
    
    @api.constrains('waste_factor')
    def _check_waste_factor(self):
        """Validate waste factor"""
        for record in self:
            if record.waste_factor < 0 or record.waste_factor > 100:
                raise ValidationError(_('Waste factor must be between 0 and 100.'))
    
    @api.constrains('efficiency_factor')
    def _check_efficiency_factor(self):
        """Validate efficiency factor"""
        for record in self:
            if record.efficiency_factor < 0 or record.efficiency_factor > 1:
                raise ValidationError(_('Efficiency factor must be between 0 and 1.'))
    
    # Methods for compatibility with existing models
    def get_material_data(self):
        """Get material data for compatibility with label.carta model"""
        if not self.is_label_material:
            return {}
        
        return {
            'name': self.name,
            'code': self.default_code,
            'paper_type': self.paper_type,
            'grammage': self.grammage,
            'thickness': self.thickness,
            'adhesive_type': self.adhesive_type,
            'adhesive_strength': self.adhesive_strength,
            'max_width': self.max_width,
            'max_length': self.max_length,
            'cost_per_sqm': self.list_price,
            'waste_factor': self.waste_factor,
            'minimum_order_quantity': self.minimum_order_quantity,
            'roll_width_standard': self.roll_width_standard,
            'roll_length_standard': self.roll_length_standard,
            'liner_type': self.liner_type,
            'liner_thickness': self.liner_thickness,
            'print_compatibility': self.print_compatibility,
            'temperature_range_min': self.temperature_range_min,
            'temperature_range_max': self.temperature_range_max,
            'shelf_life_months': self.shelf_life_months,
        }
    
    def get_machine_data(self):
        """Get machine data for compatibility with label.macchina model"""
        if not self.is_label_machine:
            return {}
        
        return {
            'name': self.name,
            'code': self.default_code,
            'machine_type': self.machine_type,
            'max_web_width': self.max_web_width,
            'max_speed': self.max_speed,
            'min_web_width': self.min_web_width,
            'min_speed': self.min_speed,
            'setup_time': self.setup_time,
            'die_change_time': self.die_change_time,
            'material_change_time': self.material_change_time,
            'warm_up_time': self.warm_up_time,
            'max_tracks': self.max_tracks,
            'precision_rating': self.precision_rating,
            'quality_factor': self.quality_factor,
            'setup_cost_per_hour': self.setup_cost_per_hour,
            'production_cost_per_hour': self.production_cost_per_hour,
            'overhead_percentage': self.overhead_percentage,
            'efficiency_factor': self.efficiency_factor,
            'maintenance_cost_per_month': self.maintenance_cost_per_month,
            'depreciation_cost_per_month': self.depreciation_cost_per_month,
            'energy_cost_per_hour': self.energy_cost_per_hour,
            'operator_cost_per_hour': self.operator_cost_per_hour,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'location': self.location,
        }
    
    def get_die_data(self):
        """Get die data for compatibility with label.fustella model"""
        if not self.is_label_die:
            return {}
        
        return {
            'name': self.name,
            'code': self.default_code,
            'die_type': self.die_type,
            'width': self.die_width,
            'length': self.die_length,
            'repeat_length': self.repeat_length,
            'max_tracks': self.die_max_tracks,
            'cutting_force_required': self.cutting_force_required,
            'stripping_difficulty': self.stripping_difficulty,
            'expected_lifetime_cuts': self.expected_lifetime_cuts,
            'current_usage_count': self.current_usage_count,
            'cost_per_use': self.cost_per_use,
            'setup_time': self.setup_time_die,
        }
