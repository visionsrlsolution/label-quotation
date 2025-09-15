# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import math


class LabelQuotation(models.Model):
    _name = 'label.quotation'
    _description = 'Label Quotation'
    _order = 'create_date desc'

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
        required=True
    )
    
    date = fields.Date(
        string='Quotation Date',
        default=fields.Date.today,
        required=True
    )
    
    valid_until = fields.Date(
        string='Valid Until',
        required=True,
        default=lambda self: fields.Date.today() + fields.timedelta(days=self.env['label.config'].get_default_validity_days())
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='draft', tracking=True)
    
    # Label Specifications
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
        default=lambda self: self.env['label.config'].get_default_interspace(),
        help='Space between labels in millimeters'
    )
    
    tracks = fields.Integer(
        string='Number of Tracks',
        default=1,
        help='Number of label tracks across the web'
    )
    
    # Material Selection
    carta_id = fields.Many2one(
        'label.carta',
        string='Paper Material',
        required=True
    )
    
    fustella_id = fields.Many2one(
        'label.fustella',
        string='Die',
        required=True
    )
    
    macchina_id = fields.Many2one(
        'label.macchina',
        string='Machine',
        required=True
    )
    
    # Quantities
    total_quantity = fields.Integer(
        string='Total Quantity (Labels)',
        required=True,
        help='Total number of labels to produce'
    )
    
    linear_length = fields.Float(
        string='Linear Length (m)',
        compute='_compute_linear_length',
        store=True,
        help='Total linear length in meters'
    )
    
    # Calculated Fields
    label_area_sqm = fields.Float(
        string='Label Area (m²)',
        compute='_compute_areas',
        store=True,
        help='Area of one label in square meters'
    )
    
    total_area_sqm = fields.Float(
        string='Total Area (m²)',
        compute='_compute_areas',
        store=True,
        help='Total area of all labels in square meters'
    )
    
    web_width = fields.Float(
        string='Web Width (mm)',
        compute='_compute_web_width',
        store=True,
        help='Required web width in millimeters'
    )
    
    yield_percentage = fields.Float(
        string='Yield Percentage (%)',
        compute='_compute_yield',
        store=True,
        help='Material yield percentage'
    )
    
    # Cost Calculations
    paper_cost = fields.Float(
        string='Paper Cost (€)',
        compute='_compute_costs',
        store=True,
        help='Total paper cost'
    )
    
    die_cost = fields.Float(
        string='Die Cost (€)',
        compute='_compute_costs',
        store=True,
        help='Total die cost (amortized)'
    )
    
    machine_cost = fields.Float(
        string='Machine Cost (€)',
        compute='_compute_costs',
        store=True,
        help='Total machine cost including setup'
    )
    
    total_cost = fields.Float(
        string='Total Cost (€)',
        compute='_compute_costs',
        store=True,
        help='Total production cost'
    )
    
    cost_per_label = fields.Float(
        string='Cost per Label (€)',
        compute='_compute_costs',
        store=True,
        help='Cost per individual label'
    )
    
    cost_per_sqm = fields.Float(
        string='Cost per m² (€)',
        compute='_compute_costs',
        store=True,
        help='Cost per square meter'
    )
    
    # Pricing
    margin_percentage = fields.Float(
        string='Margin Percentage (%)',
        default=lambda self: self.env['label.config'].get_default_margin(),
        help='Profit margin percentage'
    )
    
    selling_price = fields.Float(
        string='Selling Price (€)',
        compute='_compute_selling_price',
        store=True,
        help='Final selling price'
    )
    
    price_per_label = fields.Float(
        string='Price per Label (€)',
        compute='_compute_selling_price',
        store=True,
        help='Selling price per individual label'
    )
    
    # Additional Information
    notes = fields.Text(
        string='Notes',
        help='Additional notes for the quotation'
    )
    
    sale_order_id = fields.Many2one(
        'sale.order',
        string='Sale Order',
        readonly=True,
        help='Related sale order if quotation is accepted'
    )

    @api.model
    def create(self, vals):
        """Generate quotation number"""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('label.quotation') or _('New')
        return super().create(vals)

    @api.depends('label_width', 'label_height', 'total_quantity')
    def _compute_areas(self):
        """Calculate label and total areas"""
        for record in self:
            if record.label_width and record.label_height:
                # Area of one label in square meters
                record.label_area_sqm = (record.label_width * record.label_height) / 1000000
                # Total area for all labels
                record.total_area_sqm = record.label_area_sqm * record.total_quantity
            else:
                record.label_area_sqm = 0.0
                record.total_area_sqm = 0.0

    @api.depends('label_width', 'tracks', 'interspace')
    def _compute_web_width(self):
        """Calculate required web width"""
        for record in self:
            if record.label_width and record.tracks:
                # Web width = (label_width * tracks) + (interspace * (tracks - 1))
                record.web_width = (record.label_width * record.tracks) + (record.interspace * (record.tracks - 1))
            else:
                record.web_width = 0.0

    @api.depends('label_width', 'label_height', 'interspace')
    def _compute_yield(self):
        """Calculate material yield percentage"""
        for record in self:
            if record.label_width and record.label_height and record.interspace:
                # Calculate area per label including interspace
                total_area_per_label = (record.label_width + record.interspace) * (record.label_height + record.interspace)
                label_area = record.label_width * record.label_height
                if total_area_per_label > 0:
                    record.yield_percentage = (label_area / total_area_per_label) * 100
                else:
                    record.yield_percentage = 0.0
            else:
                record.yield_percentage = 0.0

    @api.depends('total_quantity', 'label_height', 'interspace')
    def _compute_linear_length(self):
        """Calculate total linear length"""
        for record in self:
            if record.total_quantity and record.label_height and record.interspace:
                # Linear length = (number of labels * label height) + ((number of labels - 1) * interspace)
                record.linear_length = (record.total_quantity * record.label_height + 
                                      (record.total_quantity - 1) * record.interspace) / 1000  # Convert to meters
            else:
                record.linear_length = 0.0

    @api.depends('total_area_sqm', 'carta_id', 'fustella_id', 'macchina_id', 'linear_length', 'total_quantity')
    def _compute_costs(self):
        """Calculate all costs"""
        for record in self:
            # Paper cost
            if record.carta_id and record.total_area_sqm:
                record.paper_cost = record.total_area_sqm * record.carta_id.cost_per_sqm
            else:
                record.paper_cost = 0.0
            
            # Die cost (amortized)
            if record.fustella_id and record.total_quantity:
                record.die_cost = record.fustella_id.amortized_cost_per_unit * record.total_quantity
            else:
                record.die_cost = 0.0
            
            # Machine cost
            if record.macchina_id and record.linear_length:
                record.machine_cost = record.macchina_id.calculate_production_cost(record.linear_length)
            else:
                record.machine_cost = 0.0
            
            # Total cost
            record.total_cost = record.paper_cost + record.die_cost + record.machine_cost
            
            # Cost per label
            if record.total_quantity > 0:
                record.cost_per_label = record.total_cost / record.total_quantity
            else:
                record.cost_per_label = 0.0
            
            # Cost per square meter
            if record.total_area_sqm > 0:
                record.cost_per_sqm = record.total_cost / record.total_area_sqm
            else:
                record.cost_per_sqm = 0.0

    @api.depends('total_cost', 'margin_percentage')
    def _compute_selling_price(self):
        """Calculate selling price with margin"""
        for record in self:
            if record.total_cost > 0:
                record.selling_price = record.total_cost * (1 + record.margin_percentage / 100)
            else:
                record.selling_price = 0.0
            
            # Price per label
            if record.total_quantity > 0:
                record.price_per_label = record.selling_price / record.total_quantity
            else:
                record.price_per_label = 0.0

    @api.constrains('label_width', 'label_height', 'total_quantity', 'interspace')
    def _check_positive_values(self):
        """Ensure positive values for numeric fields"""
        for record in self:
            if record.label_width <= 0:
                raise ValidationError(_('Label width must be positive'))
            if record.label_height <= 0:
                raise ValidationError(_('Label height must be positive'))
            if record.total_quantity <= 0:
                raise ValidationError(_('Total quantity must be positive'))
            if record.interspace < 0:
                raise ValidationError(_('Interspace cannot be negative'))

    @api.constrains('web_width', 'carta_id', 'macchina_id')
    def _check_web_width_limits(self):
        """Check web width against material and machine limits"""
        for record in self:
            if record.web_width > 0:
                if record.carta_id and record.web_width > record.carta_id.max_width:
                    raise ValidationError(_('Web width exceeds paper material maximum width'))
                if record.macchina_id and record.web_width > record.macchina_id.max_web_width:
                    raise ValidationError(_('Web width exceeds machine maximum width'))

    def action_send_quotation(self):
        """Send quotation to customer"""
        self.write({'state': 'sent'})
        # Here you could add email functionality
        return True

    def action_accept_quotation(self):
        """Accept quotation and create sale order"""
        self.write({'state': 'accepted'})
        # Create sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'date_order': fields.Date.today(),
            'label_quotation_id': self.id,
        })
        
        # Create sale order line
        self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self._get_or_create_label_product().id,
            'name': f'Labels {self.label_width}x{self.label_height}mm - {self.total_quantity} pcs',
            'product_uom_qty': self.total_quantity,
            'price_unit': self.price_per_label,
        })
        
        self.sale_order_id = sale_order.id
        return {
            'type': 'ir.actions.act_window',
            'name': _('Sale Order'),
            'res_model': 'sale.order',
            'res_id': sale_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_reject_quotation(self):
        """Reject quotation"""
        self.write({'state': 'rejected'})
        return True

    def action_cancel_quotation(self):
        """Cancel quotation"""
        self.write({'state': 'cancelled'})
        return True

    def _get_or_create_label_product(self):
        """Get or create a product for the label"""
        product_name = f'Label {self.label_width}x{self.label_height}mm'
        product = self.env['product.product'].search([
            ('name', '=', product_name),
            ('type', '=', 'product')
        ], limit=1)
        
        if not product:
            product = self.env['product.product'].create({
                'name': product_name,
                'type': 'product',
                'categ_id': self.env.ref('product.product_category_all').id,
                'list_price': self.price_per_label,
            })
        
        return product

    def get_quotation_summary(self):
        """Get quotation summary for reports"""
        return {
            'quotation_number': self.name,
            'customer': self.partner_id.name,
            'date': self.date,
            'label_dimensions': f"{self.label_width}x{self.label_height}mm",
            'quantity': self.total_quantity,
            'total_cost': self.total_cost,
            'selling_price': self.selling_price,
            'margin': self.margin_percentage,
            'yield': self.yield_percentage,
        }

    def action_generate_pdf(self):
        """Generate PDF report for this quotation"""
        report_generator = self.env['label.quotation.report']
        return report_generator.action_generate_pdf(self.id)
