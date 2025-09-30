# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LabelFustella(models.Model):
    _name = 'label.fustella'
    _description = 'Die Cutting Tool'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True,
        help='Name of the die cutting tool'
    )
    
    code = fields.Char(
        string='Code',
        help='Internal code for the die'
    )
    
    die_type = fields.Selection([
        ('flatbed', 'Flatbed'),
        ('rotary', 'Rotary'),
        ('laser', 'Laser'),
        ('kiss_cut', 'Kiss Cut'),
    ], string='Die Type', required=True)
    
    width = fields.Float(
        string='Width (mm)',
        help='Width of the die in millimeters'
    )
    
    length = fields.Float(
        string='Length (mm)',
        help='Length of the die in millimeters'
    )
    
    # Production Configuration
    repeat_length = fields.Float(
        string='Repeat Length (mm)',
        help='Length of one die repeat in millimeters'
    )
    
    max_tracks = fields.Integer(
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
    
    material_compatibility = fields.Many2many(
        'label.carta',
        'die_material_rel',
        'die_id',
        'material_id',
        string='Compatible Materials',
        help='Materials that work well with this die'
    )
    
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
    
    depreciation_per_use = fields.Float(
        string='Depreciation per Use (€)',
        compute='_compute_depreciation_per_use',
        help='Depreciation cost per use based on lifetime'
    )
    
    setup_time = fields.Float(
        string='Setup Time (hours)',
        help='Time required to setup the die'
    )
    
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier_rank', '>', 0)],
        help='Supplier of the die'
    )
    
    supplier_code = fields.Char(
        string='Supplier Code',
        help='Supplier reference code'
    )
    
    purchase_date = fields.Date(
        string='Purchase Date',
        help='Date when the die was purchased'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the die'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='Uncheck to archive this die'
    )
    
    # Computed fields for statistics
    quotation_count = fields.Integer(
        string='Quotation Count',
        compute='_compute_quotation_count'
    )
    
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
    
    @api.depends()
    def _compute_quotation_count(self):
        """Compute the number of quotations using this die"""
        for record in self:
            record.quotation_count = self.env['label.quotation'].search_count([
                ('fustella_id', '=', record.id)
            ])
    
    def action_view_quotations(self):
        """Action to view quotations using this die"""
        action = self.env.ref('label_quotation.action_label_quotation').read()[0]
        action['domain'] = [('fustella_id', '=', self.id)]
        action['context'] = {'default_fustella_id': self.id}
        return action
    
    def toggle_active(self):
        """Toggle active status"""
        for record in self:
            record.active = not record.active
