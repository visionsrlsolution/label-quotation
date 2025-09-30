# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class LabelQuotation(models.Model):
    _name = 'label.quotation'
    _description = 'Label Quotation'
    _rec_name = 'name'
    _order = 'date desc, name desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _check_company_auto = True

    name = fields.Char(
        string='Quotation Number',
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _('New')
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True
    )
    
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    valid_until = fields.Date(
        string='Valid Until',
        required=True,
        tracking=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        tracking=True
    )
    
    # Label Specifications
    label_width = fields.Float(
        string='Label Width (mm)',
        required=True,
        help='Width of individual labels in millimeters'
    )
    
    label_height = fields.Float(
        string='Label Height (mm)',
        required=True,
        help='Height of individual labels in millimeters'
    )
    
    interspace = fields.Float(
        string='Interspace (mm)',
        default=lambda self: self.env['label.config'].get_default_interspace(),
        help='Space between labels in millimeters'
    )
    
    tracks = fields.Integer(
        string='Number of Tracks',
        required=True,
        default=1,
        help='Number of label tracks across the web'
    )
    
    total_quantity = fields.Integer(
        string='Total Quantity',
        required=True,
        help='Total number of labels to produce'
    )
    
    # Material and Equipment
    carta_id = fields.Many2one(
        'label.carta',
        string='Paper Material',
        required=True,
        tracking=True
    )
    
    fustella_id = fields.Many2one(
        'label.fustella',
        string='Die',
        required=True,
        tracking=True
    )
    
    macchina_id = fields.Many2one(
        'label.macchina',
        string='Machine',
        required=True,
        tracking=True
    )
    
    # Calculated Fields
    linear_length = fields.Float(
        string='Linear Length (m)',
        compute='_compute_dimensions',
        store=True,
        help='Total linear length of labels in meters'
    )
    
    web_width = fields.Float(
        string='Web Width (mm)',
        compute='_compute_dimensions',
        store=True,
        help='Total web width required'
    )
    
    label_area_sqm = fields.Float(
        string='Label Area (m²)',
        compute='_compute_dimensions',
        store=True,
        help='Area of a single label in square meters'
    )
    
    total_area_sqm = fields.Float(
        string='Total Area (m²)',
        compute='_compute_dimensions',
        store=True,
        help='Total area of all labels in square meters'
    )
    
    yield_percentage = fields.Float(
        string='Material Yield (%)',
        compute='_compute_dimensions',
        store=True,
        help='Percentage of material utilization'
    )
    
    # Cost Calculation
    paper_cost = fields.Float(
        string='Paper Cost (€)',
        compute='_compute_costs',
        store=True
    )
    
    die_cost = fields.Float(
        string='Die Cost (€)',
        compute='_compute_costs',
        store=True
    )
    
    machine_cost = fields.Float(
        string='Machine Cost (€)',
        compute='_compute_costs',
        store=True
    )
    
    total_cost = fields.Float(
        string='Total Cost (€)',
        compute='_compute_costs',
        store=True
    )
    
    cost_per_label = fields.Float(
        string='Cost per Label (€)',
        compute='_compute_costs',
        store=True
    )
    
    cost_per_sqm = fields.Float(
        string='Cost per m² (€)',
        compute='_compute_costs',
        store=True
    )
    
    # Pricing
    margin_percentage = fields.Float(
        string='Margin (%)',
        default=lambda self: self.env['label.config'].get_default_margin(),
        help='Profit margin percentage'
    )
    
    selling_price = fields.Float(
        string='Selling Price (€)',
        compute='_compute_selling_price',
        store=True
    )
    
    price_per_label = fields.Float(
        string='Price per Label (€)',
        compute='_compute_selling_price',
        store=True
    )
    
    # Related Records
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        readonly=True,
        help='Sale order created from this quotation'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes for the quotation'
    )
    
    @api.depends('label_width', 'label_height', 'interspace', 'tracks', 'total_quantity', 'carta_id', 'fustella_id', 'macchina_id')
    def _compute_dimensions(self):
        """Compute label dimensions and material requirements with advanced production calculations"""
        for record in self:
            if record.label_width and record.label_height and record.total_quantity:
                # Single label area in square meters
                record.label_area_sqm = (record.label_width * record.label_height) / 1000000
                
                # Total area of just the labels (without waste)
                record.total_area_sqm = record.label_area_sqm * record.total_quantity
                
                # Advanced production calculations
                calculation_result = record._calculate_optimal_production_parameters()
                
                record.linear_length = calculation_result['linear_length']
                record.web_width = calculation_result['web_width']
                record.yield_percentage = calculation_result['yield_percentage']
                
            else:
                record.label_area_sqm = 0
                record.total_area_sqm = 0
                record.linear_length = 0
                record.web_width = 0
                record.yield_percentage = 0
    
    def _calculate_optimal_production_parameters(self):
        """Calculate optimal production parameters considering all constraints"""
        self.ensure_one()
        
        # Get configuration values
        config = self.env['label.config'].search([], limit=1)
        min_yield = config.min_yield_percentage if config else 80.0
        
        # Basic calculations
        edge_margin = 5.0  # 5mm edge margin on each side
        
        # Check machine constraints
        max_tracks_by_machine = self.macchina_id.max_tracks if self.macchina_id else 10
        effective_tracks = min(self.tracks, max_tracks_by_machine)
        
        # Check die constraints
        max_tracks_by_die = self.fustella_id.max_tracks if self.fustella_id else 10
        effective_tracks = min(effective_tracks, max_tracks_by_die)
        
        # Calculate web width with constraints
        web_width = (self.label_width * effective_tracks) + (self.interspace * (effective_tracks - 1)) + (2 * edge_margin)
        
        # Check material width constraints
        if self.carta_id and self.carta_id.max_width:
            if web_width > self.carta_id.max_width:
                # Recalculate with maximum possible tracks
                max_possible_tracks = int((self.carta_id.max_width - 2 * edge_margin + self.interspace) / (self.label_width + self.interspace))
                effective_tracks = min(max_possible_tracks, effective_tracks)
                web_width = (self.label_width * effective_tracks) + (self.interspace * (effective_tracks - 1)) + (2 * edge_margin)
        
        # Calculate linear length considering die repeat
        if self.fustella_id and self.fustella_id.repeat_length:
            die_repeat = self.fustella_id.repeat_length / 1000  # Convert to meters
            labels_per_repeat = max(1, int(die_repeat * 1000 / (self.label_height + self.interspace)))
            labels_per_meter = labels_per_repeat / die_repeat
        else:
            labels_per_meter = 1000 / (self.label_height + self.interspace)
        
        total_labels_per_meter = labels_per_meter * effective_tracks
        linear_length = self.total_quantity / total_labels_per_meter if total_labels_per_meter > 0 else 0
        
        # Calculate yield percentage with advanced factors
        yield_percentage = self._calculate_advanced_yield(web_width, linear_length, effective_tracks)
        
        return {
            'linear_length': linear_length,
            'web_width': web_width,
            'yield_percentage': yield_percentage,
            'effective_tracks': effective_tracks
        }
    
    def _calculate_advanced_yield(self, web_width, linear_length, effective_tracks):
        """Calculate yield percentage considering multiple factors"""
        self.ensure_one()
        
        base_yield = 95.0  # Start with 95% base yield
        
        # Material waste factor
        if self.carta_id and hasattr(self.carta_id, 'waste_factor'):
            material_waste = self.carta_id.waste_factor or 5.0
            base_yield -= material_waste
        
        # Width efficiency factor
        if self.carta_id and self.carta_id.max_width:
            width_efficiency = web_width / self.carta_id.max_width
            if width_efficiency < 0.6:
                base_yield -= 10  # Penalty for low width utilization
            elif width_efficiency < 0.8:
                base_yield -= 5   # Small penalty for medium utilization
        
        # Die cutting difficulty factor
        if self.fustella_id and hasattr(self.fustella_id, 'stripping_difficulty'):
            difficulty_penalties = {
                'easy': 0,
                'medium': 2,
                'difficult': 5,
                'very_difficult': 10
            }
            penalty = difficulty_penalties.get(self.fustella_id.stripping_difficulty, 2)
            base_yield -= penalty
        
        # Small run penalty (less efficient setup to production ratio)
        if linear_length < 100:  # Less than 100 meters
            base_yield -= 5
        elif linear_length < 500:  # Less than 500 meters
            base_yield -= 2
        
        # Track optimization bonus/penalty
        if effective_tracks == 1:
            base_yield -= 3  # Single track is less efficient
        elif effective_tracks >= 4:
            base_yield += 2  # Multi-track bonus
        
        return max(0, min(100, base_yield))
    
    @api.depends('total_area_sqm', 'carta_id', 'fustella_id', 'macchina_id', 'linear_length', 'yield_percentage')
    def _compute_costs(self):
        """Compute material and production costs with advanced calculations"""
        for record in self:
            # Enhanced paper cost calculation with waste
            if record.carta_id and record.total_area_sqm:
                # Calculate actual material needed including waste
                waste_multiplier = 1.0
                if record.yield_percentage > 0:
                    waste_multiplier = 100.0 / record.yield_percentage
                
                actual_material_area = record.total_area_sqm * waste_multiplier
                record.paper_cost = actual_material_area * record.carta_id.cost_per_sqm
            else:
                record.paper_cost = 0
            
            # Enhanced die cost calculation
            if record.fustella_id:
                base_die_cost = record.fustella_id.cost_per_use or 0
                
                # Add depreciation cost if available
                if hasattr(record.fustella_id, 'depreciation_per_use'):
                    base_die_cost += record.fustella_id.depreciation_per_use or 0
                
                # Apply stripping difficulty multiplier
                if hasattr(record.fustella_id, 'stripping_difficulty'):
                    difficulty_multipliers = {
                        'easy': 1.0,
                        'medium': 1.1,
                        'difficult': 1.3,
                        'very_difficult': 1.5
                    }
                    multiplier = difficulty_multipliers.get(record.fustella_id.stripping_difficulty, 1.1)
                    base_die_cost *= multiplier
                
                record.die_cost = base_die_cost
            else:
                record.die_cost = 0
            
            # Enhanced machine cost calculation based on production time
            if record.macchina_id and record.linear_length:
                # Calculate production time in hours
                machine_speed = record.macchina_id.max_speed or 100  # m/min
                efficiency = record.macchina_id.efficiency_factor or 0.85
                effective_speed = machine_speed * efficiency  # Adjusted for efficiency
                
                production_time_hours = record.linear_length / (effective_speed * 60)
                
                # Setup time
                setup_time_hours = (record.macchina_id.setup_time or 30) / 60  # Convert minutes to hours
                if hasattr(record.macchina_id, 'die_change_time'):
                    setup_time_hours += (record.macchina_id.die_change_time or 0) / 60
                if hasattr(record.macchina_id, 'material_change_time'):
                    setup_time_hours += (record.macchina_id.material_change_time or 0) / 60
                
                total_time_hours = production_time_hours + setup_time_hours
                
                # Calculate machine costs
                setup_cost = setup_time_hours * (record.macchina_id.setup_cost_per_hour or 0)
                production_cost = production_time_hours * (record.macchina_id.production_cost_per_hour or 0)
                energy_cost = total_time_hours * (record.macchina_id.energy_cost_per_hour or 0)
                operator_cost = total_time_hours * (record.macchina_id.operator_cost_per_hour or 0)
                
                # Apply overhead
                base_machine_cost = setup_cost + production_cost + energy_cost + operator_cost
                overhead_multiplier = 1 + (record.macchina_id.overhead_percentage or 0) / 100
                
                record.machine_cost = base_machine_cost * overhead_multiplier
            else:
                record.machine_cost = 0
            
            # Total cost
            record.total_cost = record.paper_cost + record.die_cost + record.machine_cost
            
            # Cost per label and per square meter
            if record.total_quantity:
                record.cost_per_label = record.total_cost / record.total_quantity
            else:
                record.cost_per_label = 0
            
            if record.total_area_sqm:
                record.cost_per_sqm = record.total_cost / record.total_area_sqm
            else:
                record.cost_per_sqm = 0
    
    @api.depends('total_cost', 'margin_percentage')
    def _compute_selling_price(self):
        """Compute selling price with margin"""
        for record in self:
            if record.total_cost and record.margin_percentage:
                record.selling_price = record.total_cost * (1 + record.margin_percentage / 100)
            else:
                record.selling_price = record.total_cost or 0
            
            if record.total_quantity:
                record.price_per_label = record.selling_price / record.total_quantity
            else:
                record.price_per_label = 0
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate quotation number on creation"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('label.quotation') or _('New')
            
            # Set default validity date
            if not vals.get('valid_until'):
                config = self.env['label.config'].get_config()
                vals['valid_until'] = fields.Date.today() + timedelta(days=config.default_quotation_validity_days)
        
        return super().create(vals_list)
    
    def action_send_quotation(self):
        """Send quotation to customer"""
        self.write({'state': 'sent'})
        # Here you could add email functionality
    
    def action_accept_quotation(self):
        """Accept quotation"""
        self.write({'state': 'accepted'})
        # Here you could create a sale order
    
    def action_reject_quotation(self):
        """Reject quotation"""
        self.write({'state': 'rejected'})
    
    def action_cancel_quotation(self):
        """Cancel quotation"""
        self.write({'state': 'cancelled'})
    
    def action_generate_pdf(self):
        """Generate PDF quotation"""
        return self.env['label.quotation.report'].action_generate_pdf(self.id)
    
    # Validation constraints
    @api.constrains('label_width', 'label_height', 'carta_id', 'macchina_id')
    def _check_material_machine_compatibility(self):
        """Validate that label dimensions are compatible with material and machine"""
        for record in self:
            if record.carta_id and record.label_width and record.label_height:
                # Check if label fits on material
                if record.carta_id.max_width and record.label_width > record.carta_id.max_width:
                    raise ValidationError(_(
                        'Label width ({}mm) exceeds material maximum width ({}mm) for {}'
                    ).format(record.label_width, record.carta_id.max_width, record.carta_id.name))
                
                if record.carta_id.max_length and record.label_height > record.carta_id.max_length:
                    raise ValidationError(_(
                        'Label height ({}mm) exceeds material maximum length ({}mm) for {}'
                    ).format(record.label_height, record.carta_id.max_length, record.carta_id.name))
            
            # Check machine constraints
            if record.macchina_id and record.web_width:
                if record.macchina_id.max_web_width and record.web_width > record.macchina_id.max_web_width:
                    raise ValidationError(_(
                        'Required web width ({}mm) exceeds machine maximum width ({}mm) for {}'
                    ).format(record.web_width, record.macchina_id.max_web_width, record.macchina_id.name))
    
    @api.constrains('tracks', 'macchina_id', 'fustella_id')
    def _check_tracks_compatibility(self):
        """Validate track count against machine and die capabilities"""
        for record in self:
            if record.tracks:
                # Check machine track limits
                if record.macchina_id and hasattr(record.macchina_id, 'max_tracks'):
                    if record.macchina_id.max_tracks and record.tracks > record.macchina_id.max_tracks:
                        raise ValidationError(_(
                            'Number of tracks ({}) exceeds machine capability ({}) for {}'
                        ).format(record.tracks, record.macchina_id.max_tracks, record.macchina_id.name))
                
                # Check die track limits
                if record.fustella_id and hasattr(record.fustella_id, 'max_tracks'):
                    if record.fustella_id.max_tracks and record.tracks > record.fustella_id.max_tracks:
                        raise ValidationError(_(
                            'Number of tracks ({}) exceeds die capability ({}) for {}'
                        ).format(record.tracks, record.fustella_id.max_tracks, record.fustella_id.name))
    
    @api.constrains('yield_percentage')
    def _check_yield_percentage(self):
        """Validate yield percentage is within acceptable range"""
        for record in self:
            if record.yield_percentage is not False:  # Allow 0% yield for error indication
                config = self.env['label.config'].search([], limit=1)
                min_yield = config.min_yield_percentage if config else 80.0
                
                if record.yield_percentage < min_yield:
                    raise ValidationError(_(
                        'Material yield ({}%) is below minimum acceptable yield ({}%). '
                        'Consider adjusting the configuration to improve efficiency.'
                    ).format(record.yield_percentage, min_yield))
    
    @api.constrains('total_quantity')
    def _check_minimum_order_quantity(self):
        """Check if quantity meets material minimum requirements"""
        for record in self:
            if record.carta_id and hasattr(record.carta_id, 'minimum_order_quantity'):
                if record.carta_id.minimum_order_quantity and record.linear_length:
                    if record.linear_length < record.carta_id.minimum_order_quantity:
                        raise ValidationError(_(
                            'Linear length required ({}m) is below minimum order quantity ({}m) for {}'
                        ).format(record.linear_length, record.carta_id.minimum_order_quantity, record.carta_id.name))
    
    @api.constrains('carta_id', 'fustella_id')
    def _check_material_die_compatibility(self):
        """Check if material is compatible with selected die"""
        for record in self:
            if record.carta_id and record.fustella_id and hasattr(record.fustella_id, 'material_compatibility'):
                compatible_materials = record.fustella_id.material_compatibility
                if compatible_materials and record.carta_id not in compatible_materials:
                    # This is a warning, not a hard constraint
                    # Could be implemented as a warning message instead
                    pass  # Allow but could log a warning
