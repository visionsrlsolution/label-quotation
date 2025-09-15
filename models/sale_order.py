# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    label_quotation_id = fields.Many2one(
        'label.quotation',
        string='Label Quotation',
        help='Related label quotation'
    )
    
    is_label_order = fields.Boolean(
        string='Is Label Order',
        compute='_compute_is_label_order',
        store=True,
        help='Indicates if this order is for label production'
    )
    
    label_quotation_count = fields.Integer(
        string='Label Quotations',
        compute='_compute_label_quotation_count',
        help='Number of related label quotations'
    )

    @api.depends('label_quotation_id')
    def _compute_is_label_order(self):
        """Check if this is a label order"""
        for order in self:
            order.is_label_order = bool(order.label_quotation_id)

    @api.depends('partner_id')
    def _compute_label_quotation_count(self):
        """Count label quotations for this customer"""
        for order in self:
            if order.partner_id:
                order.label_quotation_count = self.env['label.quotation'].search_count([
                    ('partner_id', '=', order.partner_id.id)
                ])
            else:
                order.label_quotation_count = 0

    def action_view_label_quotations(self):
        """View label quotations for this customer"""
        action = self.env.ref('label_quotation.action_label_quotation').read()[0]
        action['domain'] = [('partner_id', '=', self.partner_id.id)]
        action['context'] = {'default_partner_id': self.partner_id.id}
        return action

    def action_create_label_quotation(self):
        """Create a new label quotation from this sale order"""
        quotation = self.env['label.quotation'].create({
            'partner_id': self.partner_id.id,
            'date': fields.Date.today(),
            'valid_until': fields.Date.today() + fields.timedelta(days=30),
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': _('Label Quotation'),
            'res_model': 'label.quotation',
            'res_id': quotation.id,
            'view_mode': 'form',
            'target': 'current',
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    label_quotation_id = fields.Many2one(
        'label.quotation',
        string='Label Quotation',
        related='order_id.label_quotation_id',
        store=True
    )
    
    is_label_line = fields.Boolean(
        string='Is Label Line',
        compute='_compute_is_label_line',
        store=True
    )
    
    label_width = fields.Float(
        string='Label Width (mm)',
        related='label_quotation_id.label_width',
        store=True
    )
    
    label_height = fields.Float(
        string='Label Height (mm)',
        related='label_quotation_id.label_height',
        store=True
    )
    
    label_material = fields.Char(
        string='Label Material',
        related='label_quotation_id.carta_id.name',
        store=True
    )

    @api.depends('label_quotation_id')
    def _compute_is_label_line(self):
        """Check if this line is for label production"""
        for line in self:
            line.is_label_line = bool(line.label_quotation_id)
