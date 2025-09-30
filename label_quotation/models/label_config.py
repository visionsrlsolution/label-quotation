# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class LabelConfig(models.Model):
    _name = 'label.config'
    _description = 'Label Quotation Configuration'
    _rec_name = 'display_name'
    _check_company_auto = True

    # Company field
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True,
        index=True
    )
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    # Default Values
    default_margin_percentage = fields.Float(
        string='Default Margin Percentage (%)',
        default=30.0,
        help='Default profit margin percentage for new quotations'
    )
    
    default_quotation_validity_days = fields.Integer(
        string='Default Quotation Validity (Days)',
        default=30,
        help='Default number of days for quotation validity'
    )
    
    default_interspace = fields.Float(
        string='Default Interspace (mm)',
        default=3.2,
        help='Default interspace between labels in millimeters'
    )
    
    # Calculation Settings
    min_yield_percentage = fields.Float(
        string='Minimum Yield Percentage (%)',
        default=80.0,
        help='Minimum acceptable material yield percentage'
    )
    
    max_web_width = fields.Float(
        string='Maximum Web Width (mm)',
        default=400.0,
        help='Maximum web width for production'
    )
    
    # Email Settings
    quotation_email_template_id = fields.Many2one(
        'mail.template',
        string='Quotation Email Template',
        help='Email template for sending quotations'
    )
    
    # PDF Settings
    pdf_include_logo = fields.Boolean(
        string='Include Logo in PDF',
        default=True,
        help='Include company logo in quotation PDFs'
    )
    
    pdf_logo = fields.Binary(
        string='PDF Logo',
        help='Logo to include in quotation PDFs'
    )
    
    # Approval Settings
    require_approval = fields.Boolean(
        string='Require Approval for Large Orders',
        default=True,
        help='Require approval for orders above threshold'
    )
    
    approval_threshold = fields.Float(
        string='Approval Threshold (€)',
        default=10000.0,
        help='Order value threshold requiring approval'
    )
    
    approval_user_ids = fields.Many2many(
        'res.users',
        string='Approval Users',
        help='Users who can approve large orders',
        check_company=True
    )

    # Computed fields
    @api.depends('company_id')
    def _compute_display_name(self):
        """Compute display name based on company"""
        for record in self:
            record.display_name = _('Configuration for %s') % record.company_id.name

    # Constraints
    @api.constrains('default_margin_percentage')
    def _check_margin_percentage(self):
        """Validate margin percentage"""
        for record in self:
            if record.default_margin_percentage < 0 or record.default_margin_percentage > 100:
                raise ValidationError(_('Margin percentage must be between 0 and 100.'))

    @api.constrains('default_quotation_validity_days')
    def _check_validity_days(self):
        """Validate quotation validity days"""
        for record in self:
            if record.default_quotation_validity_days <= 0:
                raise ValidationError(_('Quotation validity days must be positive.'))

    @api.constrains('default_interspace')
    def _check_interspace(self):
        """Validate interspace value"""
        for record in self:
            if record.default_interspace < 0:
                raise ValidationError(_('Interspace cannot be negative.'))

    @api.constrains('min_yield_percentage')
    def _check_yield_percentage(self):
        """Validate yield percentage"""
        for record in self:
            if record.min_yield_percentage < 0 or record.min_yield_percentage > 100:
                raise ValidationError(_('Yield percentage must be between 0 and 100.'))

    @api.constrains('max_web_width')
    def _check_web_width(self):
        """Validate web width"""
        for record in self:
            if record.max_web_width <= 0:
                raise ValidationError(_('Maximum web width must be positive.'))

    @api.constrains('approval_threshold')
    def _check_approval_threshold(self):
        """Validate approval threshold"""
        for record in self:
            if record.approval_threshold < 0:
                raise ValidationError(_('Approval threshold cannot be negative.'))

    @api.constrains('company_id')
    def _check_unique_company(self):
        """Ensure only one configuration per company"""
        for record in self:
            existing = self.search([
                ('company_id', '=', record.company_id.id),
                ('id', '!=', record.id)
            ])
            if existing:
                raise ValidationError(_('Only one configuration is allowed per company.'))

    # Model methods
    @api.model
    def get_config(self, company_id=None):
        """Get configuration for specified or current company"""
        if company_id is None:
            company_id = self.env.company.id
        
        config = self.search([('company_id', '=', company_id)], limit=1)
        if not config:
            config = self.create({'company_id': company_id})
        return config

    @api.model
    def get_default_margin(self, company_id=None):
        """Get default margin percentage"""
        return self.get_config(company_id).default_margin_percentage

    @api.model
    def get_default_validity_days(self, company_id=None):
        """Get default validity days"""
        return self.get_config(company_id).default_quotation_validity_days

    @api.model
    def get_default_interspace(self, company_id=None):
        """Get default interspace"""
        return self.get_config(company_id).default_interspace

    @api.model
    def check_approval_required(self, order_value, company_id=None):
        """Check if approval is required for order value"""
        config = self.get_config(company_id)
        return config.require_approval and order_value >= config.approval_threshold
