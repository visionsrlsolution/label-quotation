# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LabelMacchina(models.Model):
    _name = 'label.macchina'
    _description = 'Label Production Machine'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the production machine'
    )
    
    code = fields.Char(
        string='Code',
        help='Internal code for the machine'
    )
    
    machine_type = fields.Selection([
        ('vega_plus', 'Vega Plus'),
        ('digicompact', 'Digicompact'),
        ('flexo', 'Flexographic'),
        ('offset', 'Offset'),
        ('digital', 'Digital'),
        ('screen', 'Screen Printing'),
        ('gravure', 'Gravure'),
    ], string='Machine Type', required=True)
    
    max_web_width = fields.Float(
        string='Max Web Width (mm)',
        help='Maximum web width the machine can handle'
    )
    
    max_speed = fields.Float(
        string='Max Speed (m/min)',
        help='Maximum production speed in meters per minute'
    )
    
    setup_time = fields.Float(
        string='Setup Time (minutes)',
        help='Time required to setup the machine in minutes'
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
    
    # Advanced Production Configuration
    min_web_width = fields.Float(
        string='Min Web Width (mm)',
        help='Minimum web width the machine can handle'
    )
    
    min_speed = fields.Float(
        string='Min Speed (m/min)',
        help='Minimum production speed in meters per minute'
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
    
    supported_materials = fields.Many2many(
        'label.carta',
        'machine_material_rel',
        'machine_id',
        'material_id',
        string='Supported Materials',
        help='Materials that this machine can process'
    )
    
    supported_die_types = fields.Many2many(
        'label.fustella',
        'machine_die_rel',
        'machine_id',
        'die_id',
        string='Supported Die Types',
        help='Die types that this machine can use'
    )
    
    quality_factor = fields.Float(
        string='Quality Factor',
        default=1.0,
        help='Quality multiplier factor (affects pricing)'
    )
    
    # Legacy fields for backward compatibility
    hourly_cost = fields.Float(
        string='Hourly Cost (€)',
        help='Cost per hour of machine operation (legacy field)',
        compute='_compute_hourly_cost',
        store=True
    )
    
    setup_cost = fields.Float(
        string='Setup Cost (€)',
        help='Cost for machine setup (legacy field)',
        compute='_compute_setup_cost',
        store=True
    )
    
    manufacturer = fields.Char(
        string='Manufacturer',
        help='Machine manufacturer'
    )
    
    model = fields.Char(
        string='Model',
        help='Machine model'
    )
    
    serial_number = fields.Char(
        string='Serial Number',
        help='Machine serial number'
    )
    
    purchase_date = fields.Date(
        string='Purchase Date',
        help='Date when the machine was purchased'
    )
    
    installation_date = fields.Date(
        string='Installation Date',
        help='Date when the machine was installed'
    )
    
    last_maintenance_date = fields.Date(
        string='Last Maintenance Date',
        help='Date of last maintenance'
    )
    
    next_maintenance_date = fields.Date(
        string='Next Maintenance Date',
        help='Date of next scheduled maintenance'
    )
    
    location = fields.Char(
        string='Location',
        help='Physical location of the machine'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the machine'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this machine'
    )
    
    # Computed fields for legacy compatibility
    @api.depends('production_cost_per_hour', 'energy_cost_per_hour', 'operator_cost_per_hour', 'overhead_percentage')
    def _compute_hourly_cost(self):
        """Compute total hourly cost including overhead"""
        for record in self:
            base_cost = (record.production_cost_per_hour or 0) + (record.energy_cost_per_hour or 0) + (record.operator_cost_per_hour or 0)
            overhead = base_cost * (record.overhead_percentage or 0) / 100
            record.hourly_cost = base_cost + overhead
    
    @api.depends('setup_cost_per_hour', 'setup_time')
    def _compute_setup_cost(self):
        """Compute total setup cost based on time and hourly rate"""
        for record in self:
            if record.setup_time and record.setup_cost_per_hour:
                record.setup_cost = (record.setup_time / 60) * record.setup_cost_per_hour
            else:
                record.setup_cost = 0
    
    # Computed fields for statistics
    quotation_count = fields.Integer(
        string='Quotation Count',
        compute='_compute_quotation_count'
    )
    
    @api.depends()
    def _compute_quotation_count(self):
        """Compute the number of quotations using this machine"""
        for record in self:
            record.quotation_count = self.env['label.quotation'].search_count([
                ('macchina_id', '=', record.id)
            ])
    
    def action_view_quotations(self):
        """Action to view quotations using this machine"""
        action = self.env.ref('label_quotation.action_label_quotation').read()[0]
        action['domain'] = [('macchina_id', '=', self.id)]
        action['context'] = {'default_macchina_id': self.id}
        return action
    
    def toggle_active(self):
        """Toggle active status"""
        for record in self:
            record.active = not record.active
