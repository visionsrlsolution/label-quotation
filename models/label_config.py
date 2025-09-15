# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LabelConfig(models.Model):
    _name = 'label.config'
    _description = 'Label Quotation Configuration'
    _rec_name = 'company_id'

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
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
        help='Users who can approve large orders'
    )

    @api.model
    def get_config(self):
        """Get configuration for current company"""
        config = self.search([('company_id', '=', self.env.company.id)], limit=1)
        if not config:
            config = self.create({
                'company_id': self.env.company.id,
            })
        return config

    @api.model
    def get_default_margin(self):
        """Get default margin percentage"""
        return self.get_config().default_margin_percentage

    @api.model
    def get_default_validity_days(self):
        """Get default validity days"""
        return self.get_config().default_quotation_validity_days

    @api.model
    def get_default_interspace(self):
        """Get default interspace"""
        return self.get_config().default_interspace

    @api.model
    def check_approval_required(self, order_value):
        """Check if approval is required for order value"""
        config = self.get_config()
        if config.require_approval and order_value >= config.approval_threshold:
            return True
        return False
