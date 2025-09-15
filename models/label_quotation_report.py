# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import base64
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


class LabelQuotationReport(models.Model):
    _name = 'label.quotation.report'
    _description = 'Label Quotation Report Generator'

    def generate_quotation_pdf(self, quotation_id):
        """Generate PDF report for label quotation"""
        quotation = self.env['label.quotation'].browse(quotation_id)
        
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                              rightMargin=20*mm, leftMargin=20*mm,
                              topMargin=20*mm, bottomMargin=20*mm)
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        normal_style = styles['Normal']
        
        # Build PDF content
        story = []
        
        # Header
        story.append(Paragraph("PREVENTIVO ETICHETTE", title_style))
        story.append(Spacer(1, 12))
        
        # Quotation Info
        story.append(Paragraph(f"<b>Numero Preventivo:</b> {quotation.name}", normal_style))
        story.append(Paragraph(f"<b>Data:</b> {quotation.date.strftime('%d/%m/%Y')}", normal_style))
        story.append(Paragraph(f"<b>Valido fino al:</b> {quotation.valid_until.strftime('%d/%m/%Y')}", normal_style))
        story.append(Spacer(1, 20))
        
        # Customer Info
        story.append(Paragraph("DATI CLIENTE", heading_style))
        story.append(Paragraph(f"<b>Cliente:</b> {quotation.partner_id.name}", normal_style))
        if quotation.partner_id.street:
            story.append(Paragraph(f"<b>Indirizzo:</b> {quotation.partner_id.street}", normal_style))
        if quotation.partner_id.city:
            story.append(Paragraph(f"<b>Città:</b> {quotation.partner_id.city}", normal_style))
        if quotation.partner_id.vat:
            story.append(Paragraph(f"<b>P.IVA:</b> {quotation.partner_id.vat}", normal_style))
        story.append(Spacer(1, 20))
        
        # Label Specifications
        story.append(Paragraph("SPECIFICHE ETICHETTE", heading_style))
        spec_data = [
            ['Dimensione Etichetta', f"{quotation.label_width} x {quotation.label_height} mm"],
            ['Interspazio', f"{quotation.interspace} mm"],
            ['Numero Tracce', str(quotation.tracks)],
            ['Materiale', quotation.carta_id.name],
            ['Fustella', quotation.fustella_id.name],
            ['Macchina', quotation.macchina_id.name],
        ]
        
        spec_table = Table(spec_data, colWidths=[80*mm, 80*mm])
        spec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(spec_table)
        story.append(Spacer(1, 20))
        
        # Quantities and Calculations
        story.append(Paragraph("CALCOLI E QUANTITÀ", heading_style))
        calc_data = [
            ['Quantità Totale', f"{quotation.total_quantity:,} etichette"],
            ['Lunghezza Lineare', f"{quotation.linear_length:,.2f} metri"],
            ['Area Totale', f"{quotation.total_area_sqm:,.2f} m²"],
            ['Larghezza Web', f"{quotation.web_width} mm"],
            ['Resa Materiale', f"{quotation.yield_percentage:.1f}%"],
        ]
        
        calc_table = Table(calc_data, colWidths=[80*mm, 80*mm])
        calc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(calc_table)
        story.append(Spacer(1, 20))
        
        # Cost Breakdown
        story.append(Paragraph("ANALISI COSTI", heading_style))
        cost_data = [
            ['Voce', 'Importo (€)', 'Percentuale'],
            ['Costo Carta', f"{quotation.paper_cost:,.2f}", f"{(quotation.paper_cost/quotation.total_cost*100):.1f}%"],
            ['Costo Fustella', f"{quotation.die_cost:,.2f}", f"{(quotation.die_cost/quotation.total_cost*100):.1f}%"],
            ['Costo Macchina', f"{quotation.machine_cost:,.2f}", f"{(quotation.machine_cost/quotation.total_cost*100):.1f}%"],
            ['TOTALE COSTI', f"{quotation.total_cost:,.2f}", "100.0%"],
            ['', '', ''],
            ['Margine', f"{quotation.margin_percentage:.1f}%", ''],
            ['PREZZO VENDITA', f"{quotation.selling_price:,.2f}", ''],
            ['Prezzo per Etichetta', f"{quotation.price_per_label:.4f}", ''],
        ]
        
        cost_table = Table(cost_data, colWidths=[60*mm, 50*mm, 50*mm])
        cost_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ('FONTNAME', (0, 7), (-1, 7), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 4), (-1, 4), 12),
            ('FONTSIZE', (0, 7), (-1, 7), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, 3), colors.beige),
            ('BACKGROUND', (0, 4), (-1, 4), colors.lightgrey),
            ('BACKGROUND', (0, 7), (-1, 7), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(cost_table)
        story.append(Spacer(1, 20))
        
        # Notes
        if quotation.notes:
            story.append(Paragraph("NOTE", heading_style))
            story.append(Paragraph(quotation.notes, normal_style))
            story.append(Spacer(1, 20))
        
        # Footer
        story.append(Paragraph("CONDIZIONI GENERALI", heading_style))
        story.append(Paragraph("• Prezzi validi fino alla data indicata", normal_style))
        story.append(Paragraph("• Consegna secondo accordi", normal_style))
        story.append(Paragraph("• Pagamento secondo condizioni contrattuali", normal_style))
        story.append(Paragraph("• Il presente preventivo non costituisce impegno di acquisto", normal_style))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer.getvalue()

    def action_generate_pdf(self, quotation_id):
        """Action to generate and download PDF"""
        pdf_content = self.generate_quotation_pdf(quotation_id)
        
        # Create attachment
        quotation = self.env['label.quotation'].browse(quotation_id)
        attachment = self.env['ir.attachment'].create({
            'name': f'Preventivo_{quotation.name}.pdf',
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': 'label.quotation',
            'res_id': quotation_id,
            'mimetype': 'application/pdf'
        })
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'new',
        }
