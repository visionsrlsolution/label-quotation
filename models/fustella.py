# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Fustella(models.Model):
    _name = 'label.fustella'
    _description = 'Die for Label Cutting'
    _order = 'code'

    name = fields.Char(
        string='Die Name',
        required=True,
        help='Name of the die (e.g., Presente FUSTELLA 149x210mm)'
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Internal code for the die (e.g., LR1, LS17)'
    )
    
    label_width = fields.Float(
        string='Label Width (mm)',
        required=True,
        help='Width of the label in millimeters'
    )
    
    label_height = fields.Float(
        string='Label Height (mm)',
        required=True,
        help='Height of the label in millimeters'
    )
    
    interspace = fields.Float(
        string='Interspace (mm)',
        required=True,
        default=3.2,
        help='Space between labels in millimeters'
    )
    
    tracks = fields.Integer(
        string='Number of Tracks',
        default=1,
        help='Number of label tracks across the web'
    )
    
    die_type = fields.Selection([
        ('existing', 'Existing Die (Sheet Metal)'),
        ('new', 'New Die'),
        ('laser', 'Laser Cut')
    ], string='Die Type', default='existing')
    
    die_material = fields.Selection([
        ('steel', 'Steel'),
        ('aluminum', 'Aluminum'),
        ('other', 'Other')
    ], string='Die Material', default='steel')
    
    precision = fields.Float(
        string='Precision (mm)',
        default=0.1,
        help='Cutting precision in millimeters'
    )
    
    max_web_width = fields.Float(
        string='Max Web Width (mm)',
        default=400.0,
        help='Maximum web width this die can handle'
    )
    
    cost = fields.Float(
        string='Die Cost (€)',
        required=True,
        help='Fixed cost of the die in euros'
    )
    
    amortization_quantity = fields.Float(
        string='Amortization Quantity',
        default=1000000.0,
        help='Quantity over which the die cost is amortized'
    )
    
    amortized_cost_per_unit = fields.Float(
        string='Amortized Cost per Unit (€)',
        compute='_compute_amortized_cost',
        store=True,
        help='Amortized cost per label'
    )
    
    creation_date = fields.Date(
        string='Creation Date',
        default=fields.Date.today
    )
    
    last_used_date = fields.Date(
        string='Last Used Date'
    )
    
    usage_count = fields.Integer(
        string='Usage Count',
        default=0,
        help='Number of times this die has been used'
    )
    
    status = fields.Selection([
        ('present', 'Present'),
        ('erroneous', 'Erroneous'),
        ('maintenance', 'Maintenance'),
        ('retired', 'Retired')
    ], string='Status', default='present')
    
    special_features = fields.Selection([
        ('standard_heights', 'Standard Heights'),
        ('right_angle', 'Right Angle'),
        ('horizontal_scoring', 'Horizontal Scoring'),
        ('vertical_scoring', 'Vertical Scoring'),
        ('none', 'None')
    ], string='Special Features', default='none')
    
    supplier_id = fields.Many2one(
        'res.partner',
        string='Die Supplier',
        domain=[('supplier_rank', '>', 0)]
    )
    
    supplier_code = fields.Char(
        string='Supplier Code',
        help='Supplier reference code for the die'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the die'
    )

    @api.depends('cost', 'amortization_quantity')
    def _compute_amortized_cost(self):
        """Calculate amortized cost per unit"""
        for record in self:
            if record.amortization_quantity > 0:
                record.amortized_cost_per_unit = record.cost / record.amortization_quantity
            else:
                record.amortized_cost_per_unit = 0.0

    @api.constrains('label_width', 'label_height', 'interspace', 'cost')
    def _check_positive_values(self):
        """Ensure positive values for numeric fields"""
        for record in self:
            if record.label_width <= 0:
                raise ValidationError(_('Label width must be positive'))
            if record.label_height <= 0:
                raise ValidationError(_('Label height must be positive'))
            if record.interspace < 0:
                raise ValidationError(_('Interspace cannot be negative'))
            if record.cost < 0:
                raise ValidationError(_('Die cost cannot be negative'))

    @api.constrains('code')
    def _check_unique_code(self):
        """Ensure unique code"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Die code must be unique'))

    @api.constrains('max_web_width')
    def _check_web_width(self):
        """Ensure web width is within limits"""
        for record in self:
            if record.max_web_width > 400:
                raise ValidationError(_('Maximum web width cannot exceed 400mm'))

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.code} - {record.name}"
            if record.label_width and record.label_height:
                name += f" ({record.label_width}x{record.label_height}mm)"
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

    def action_update_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used_date = fields.Date.today()

    def compute_yield_percentage(self):
        """Calculate yield percentage based on label dimensions and interspace"""
        for record in self:
            if record.label_width and record.label_height and record.interspace:
                # Calculate area per label including interspace
                total_area_per_label = (record.label_width + record.interspace) * (record.label_height + record.interspace)
                label_area = record.label_width * record.label_height
                yield_pct = (label_area / total_area_per_label) * 100
                return yield_pct
            return 0.0

    def get_cost_per_sqm(self):
        """Get cost per square meter for this die"""
        if self.label_width and self.label_height:
            label_area_sqm = (self.label_width * self.label_height) / 1000000  # Convert mm² to m²
            if label_area_sqm > 0:
                return self.amortized_cost_per_unit / label_area_sqm
        return 0.0
