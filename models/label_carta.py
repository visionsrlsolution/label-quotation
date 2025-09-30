# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LabelCarta(models.Model):
    _name = 'label.carta'
    _description = 'Paper Material'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the paper material'
    )
    
    code = fields.Char(
        string='Code',
        help='Internal code for the paper material'
    )
    
    paper_type = fields.Selection([
        ('thermal', 'Thermal'),
        ('vellum', 'Vellum'),
        ('adhesive', 'Adhesive'),
        ('plain', 'Plain'),
        ('coated', 'Coated'),
        ('recycled', 'Recycled'),
    ], string='Paper Type', required=True)
    
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
    
    cost_per_sqm = fields.Float(
        string='Cost per m² (€)',
        help='Cost per square meter in euros'
    )
    
    # Production Configuration Fields
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
    
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier_rank', '>', 0)],
        help='Main supplier for this material'
    )
    
    supplier_code = fields.Char(
        string='Supplier Code',
        help='Supplier reference code for this material'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the paper material'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this material'
    )
    
    # Computed fields for statistics
    quotation_count = fields.Integer(
        string='Quotation Count',
        compute='_compute_quotation_count'
    )
    
    @api.depends()
    def _compute_quotation_count(self):
        """Compute the number of quotations using this material"""
        for record in self:
            record.quotation_count = self.env['label.quotation'].search_count([
                ('carta_id', '=', record.id)
            ])
    
    def action_view_quotations(self):
        """Action to view quotations using this material"""
        action = self.env.ref('label_quotation.action_label_quotation').read()[0]
        action['domain'] = [('carta_id', '=', self.id)]
        action['context'] = {'default_carta_id': self.id}
        return action
    
    def toggle_active(self):
        """Toggle active status"""
        for record in self:
            record.active = not record.active
