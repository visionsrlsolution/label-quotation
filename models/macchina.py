# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Macchina(models.Model):
    _name = 'label.macchina'
    _description = 'Die-Cutting Machine'
    _order = 'name'

    name = fields.Char(
        string='Machine Name',
        required=True,
        help='Name of the die-cutting machine'
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Internal code for the machine'
    )
    
    machine_type = fields.Selection([
        ('vega_plus', 'Vega+ (Prati)'),
        ('digicompact', 'Digicompact (Prati)'),
        ('other', 'Other')
    ], string='Machine Type', required=True)
    
    manufacturer = fields.Char(
        string='Manufacturer',
        default='Prati'
    )
    
    model = fields.Char(
        string='Model',
        help='Machine model (e.g., LF450)'
    )
    
    max_speed = fields.Float(
        string='Max Speed (m/min)',
        required=True,
        help='Maximum speed in meters per minute'
    )
    
    max_web_width = fields.Float(
        string='Max Web Width (mm)',
        required=True,
        help='Maximum web width in millimeters'
    )
    
    setup_time = fields.Float(
        string='Setup Time (min)',
        default=30.0,
        help='Average setup time in minutes'
    )
    
    setup_cost_per_hour = fields.Float(
        string='Setup Cost per Hour (€)',
        required=True,
        help='Setup cost per hour in euros'
    )
    
    production_cost_per_hour = fields.Float(
        string='Production Cost per Hour (€)',
        required=True,
        help='Production cost per hour in euros'
    )
    
    overhead_percentage = fields.Float(
        string='Overhead Percentage (%)',
        default=15.0,
        help='Overhead percentage for additional costs'
    )
    
    efficiency_factor = fields.Float(
        string='Efficiency Factor',
        default=0.85,
        help='Machine efficiency factor (0-1)'
    )
    
    maintenance_cost_per_month = fields.Float(
        string='Maintenance Cost per Month (€)',
        default=500.0,
        help='Monthly maintenance cost'
    )
    
    depreciation_cost_per_month = fields.Float(
        string='Depreciation Cost per Month (€)',
        default=1000.0,
        help='Monthly depreciation cost'
    )
    
    energy_cost_per_hour = fields.Float(
        string='Energy Cost per Hour (€)',
        default=5.0,
        help='Energy cost per hour of operation'
    )
    
    operator_cost_per_hour = fields.Float(
        string='Operator Cost per Hour (€)',
        default=25.0,
        help='Operator cost per hour'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    location = fields.Char(
        string='Location',
        help='Machine location in the facility'
    )
    
    installation_date = fields.Date(
        string='Installation Date'
    )
    
    last_maintenance_date = fields.Date(
        string='Last Maintenance Date'
    )
    
    next_maintenance_date = fields.Date(
        string='Next Maintenance Date'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the machine'
    )

    @api.constrains('max_speed', 'max_web_width', 'setup_time', 'efficiency_factor')
    def _check_positive_values(self):
        """Ensure positive values for numeric fields"""
        for record in self:
            if record.max_speed <= 0:
                raise ValidationError(_('Max speed must be positive'))
            if record.max_web_width <= 0:
                raise ValidationError(_('Max web width must be positive'))
            if record.setup_time < 0:
                raise ValidationError(_('Setup time cannot be negative'))
            if not 0 < record.efficiency_factor <= 1:
                raise ValidationError(_('Efficiency factor must be between 0 and 1'))

    @api.constrains('code')
    def _check_unique_code(self):
        """Ensure unique code"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Machine code must be unique'))

    @api.constrains('max_web_width')
    def _check_web_width_limits(self):
        """Check web width limits based on machine type"""
        for record in self:
            if record.machine_type == 'vega_plus' and record.max_web_width > 400:
                raise ValidationError(_('Vega+ machines cannot exceed 400mm web width'))
            elif record.machine_type == 'digicompact' and record.max_web_width > 350:
                raise ValidationError(_('Digicompact machines cannot exceed 350mm web width'))

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.code} - {record.name}"
            if record.model:
                name += f" ({record.model})"
            result.append((record.id, name))
        return result

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100):
        """Enhanced search by name or code"""
        args = args or []
        if name:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
            return self.search(domain + args, limit=limit).name_get()
        return super()._name_search(name, args, operator, limit)

    def get_total_hourly_cost(self):
        """Calculate total hourly cost including all overheads"""
        for record in self:
            # Base production cost
            total_cost = record.production_cost_per_hour
            
            # Add energy cost
            total_cost += record.energy_cost_per_hour
            
            # Add operator cost
            total_cost += record.operator_cost_per_hour
            
            # Add maintenance and depreciation (prorated per hour)
            monthly_fixed_costs = record.maintenance_cost_per_month + record.depreciation_cost_per_month
            hourly_fixed_costs = monthly_fixed_costs / (30 * 24)  # Assume 30 days, 24 hours
            total_cost += hourly_fixed_costs
            
            # Apply overhead percentage
            total_cost *= (1 + record.overhead_percentage / 100)
            
            return total_cost

    def calculate_production_time(self, linear_length_m, speed_factor=1.0):
        """Calculate production time for given linear length"""
        for record in self:
            if record.max_speed > 0:
                # Apply efficiency factor and speed factor
                effective_speed = record.max_speed * record.efficiency_factor * speed_factor
                production_time = linear_length_m / effective_speed  # in minutes
                return production_time
            return 0.0

    def calculate_setup_cost(self):
        """Calculate setup cost"""
        for record in self:
            setup_hours = record.setup_time / 60.0
            return setup_hours * record.setup_cost_per_hour

    def calculate_production_cost(self, linear_length_m, speed_factor=1.0):
        """Calculate total production cost for given linear length"""
        for record in self:
            # Setup cost
            setup_cost = record.calculate_setup_cost()
            
            # Production time and cost
            production_time = record.calculate_production_time(linear_length_m, speed_factor)
            production_hours = production_time / 60.0
            production_cost = production_hours * record.get_total_hourly_cost()
            
            return setup_cost + production_cost

    def get_capacity_info(self):
        """Get machine capacity information"""
        for record in self:
            return {
                'max_speed': record.max_speed,
                'max_web_width': record.max_web_width,
                'efficiency': record.efficiency_factor,
                'hourly_cost': record.get_total_hourly_cost(),
                'setup_time': record.setup_time,
                'setup_cost': record.calculate_setup_cost()
            }
