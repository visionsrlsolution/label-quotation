# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Carta(models.Model):
    _name = 'label.carta'
    _description = 'Paper Material for Labels'
    _order = 'name'

    name = fields.Char(
        string='Paper Name',
        required=True,
        help='Name of the paper material (e.g., Vellum Neutro FSC, Thermal FSC)'
    )
    
    code = fields.Char(
        string='Code',
        required=True,
        help='Internal code for the paper material'
    )
    
    paper_type = fields.Selection([
        ('thermal', 'Thermal'),
        ('vellum', 'Vellum'),
        ('synthetic', 'Synthetic'),
        ('other', 'Other')
    ], string='Paper Type', required=True, default='vellum')
    
    grammage = fields.Float(
        string='Grammage (g/m²)',
        required=True,
        help='Weight per square meter in grams'
    )
    
    thickness = fields.Float(
        string='Thickness (µm)',
        help='Thickness in micrometers'
    )
    
    adhesive_type = fields.Selection([
        ('hot_melt', 'Hot Melt'),
        ('acrylic', 'Acrylic'),
        ('rubber', 'Rubber'),
        ('other', 'Other')
    ], string='Adhesive Type', default='hot_melt')
    
    adhesive_strength = fields.Selection([
        ('standard', 'Standard'),
        ('strong', 'Strong'),
        ('permanent', 'Permanent'),
        ('removable', 'Removable')
    ], string='Adhesive Strength', default='standard')
    
    max_width = fields.Float(
        string='Max Width (mm)',
        default=400.0,
        help='Maximum web width in millimeters'
    )
    
    max_length = fields.Float(
        string='Max Length (m)',
        default=4000.0,
        help='Maximum length per roll in meters'
    )
    
    cost_per_sqm = fields.Float(
        string='Cost per m² (€)',
        required=True,
        help='Cost per square meter in euros'
    )
    
    supplier_id = fields.Many2one(
        'res.partner',
        string='Supplier',
        domain=[('supplier_rank', '>', 0)]
    )
    
    supplier_code = fields.Char(
        string='Supplier Code',
        help='Supplier reference code'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional notes about the paper material'
    )

    @api.constrains('grammage', 'thickness', 'cost_per_sqm')
    def _check_positive_values(self):
        """Ensure positive values for numeric fields"""
        for record in self:
            if record.grammage <= 0:
                raise ValidationError(_('Grammage must be positive'))
            if record.thickness and record.thickness <= 0:
                raise ValidationError(_('Thickness must be positive'))
            if record.cost_per_sqm <= 0:
                raise ValidationError(_('Cost per m² must be positive'))

    @api.constrains('code')
    def _check_unique_code(self):
        """Ensure unique code"""
        for record in self:
            if self.search_count([('code', '=', record.code), ('id', '!=', record.id)]) > 0:
                raise ValidationError(_('Paper code must be unique'))

    def name_get(self):
        """Custom name display"""
        result = []
        for record in self:
            name = f"{record.code} - {record.name}"
            if record.grammage:
                name += f" ({record.grammage}g/m²)"
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
