# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class ProductionAnalysisReport(models.TransientModel):
    _name = 'production.analysis.report'
    _description = 'Production Analysis Report Generator'

    # Report Parameters
    date_from = fields.Date(
        string='Date From',
        default=lambda self: fields.Date.today() - timedelta(days=30),
        required=True
    )
    
    date_to = fields.Date(
        string='Date To',
        default=fields.Date.today,
        required=True
    )
    
    report_type = fields.Selection([
        ('efficiency', 'Material Efficiency Report'),
        ('machine_utilization', 'Machine Utilization Report'),
        ('cost_analysis', 'Cost Analysis Report'),
        ('die_usage', 'Die Usage Report'),
        ('material_consumption', 'Material Consumption Report'),
    ], string='Report Type', default='efficiency', required=True)
    
    machine_ids = fields.Many2many(
        'label.macchina',
        string='Machines',
        help='Leave empty to include all machines'
    )
    
    material_ids = fields.Many2many(
        'label.carta',
        string='Materials',
        help='Leave empty to include all materials'
    )
    
    # Report Results
    report_data = fields.Text(
        string='Report Data',
        readonly=True
    )
    
    report_html = fields.Html(
        string='Report HTML',
        readonly=True
    )

    def action_generate_report(self):
        """Generate the selected report"""
        self.ensure_one()
        
        if self.date_from > self.date_to:
            raise ValidationError(_('Date From cannot be later than Date To'))
        
        # Get quotations in date range
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('state', 'in', ['sent', 'accepted'])
        ]
        
        if self.machine_ids:
            domain.append(('macchina_id', 'in', self.machine_ids.ids))
        if self.material_ids:
            domain.append(('carta_id', 'in', self.material_ids.ids))
        
        quotations = self.env['label.quotation'].search(domain)
        
        if self.report_type == 'efficiency':
            report_data = self._generate_efficiency_report(quotations)
        elif self.report_type == 'machine_utilization':
            report_data = self._generate_machine_utilization_report(quotations)
        elif self.report_type == 'cost_analysis':
            report_data = self._generate_cost_analysis_report(quotations)
        elif self.report_type == 'die_usage':
            report_data = self._generate_die_usage_report(quotations)
        elif self.report_type == 'material_consumption':
            report_data = self._generate_material_consumption_report(quotations)
        else:
            report_data = {'error': 'Unknown report type'}
        
        # Convert to HTML
        html_report = self._convert_to_html(report_data)
        
        self.write({
            'report_data': str(report_data),
            'report_html': html_report
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'production.analysis.report',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def _generate_efficiency_report(self, quotations):
        """Generate material efficiency analysis"""
        report_data = {
            'title': 'Material Efficiency Report',
            'period': f'{self.date_from} to {self.date_to}',
            'summary': {},
            'details': []
        }
        
        total_quotations = len(quotations)
        total_yield = sum(q.yield_percentage for q in quotations if q.yield_percentage)
        avg_yield = total_yield / total_quotations if total_quotations else 0
        
        # Yield by material
        material_yields = {}
        for quotation in quotations:
            if quotation.carta_id and quotation.yield_percentage:
                material = quotation.carta_id.name
                if material not in material_yields:
                    material_yields[material] = {'yields': [], 'quotations': 0}
                material_yields[material]['yields'].append(quotation.yield_percentage)
                material_yields[material]['quotations'] += 1
        
        # Calculate averages
        for material, data in material_yields.items():
            data['avg_yield'] = sum(data['yields']) / len(data['yields'])
            data['min_yield'] = min(data['yields'])
            data['max_yield'] = max(data['yields'])
        
        report_data['summary'] = {
            'total_quotations': total_quotations,
            'average_yield': round(avg_yield, 2),
            'best_material': max(material_yields.items(), key=lambda x: x[1]['avg_yield'])[0] if material_yields else None,
            'worst_material': min(material_yields.items(), key=lambda x: x[1]['avg_yield'])[0] if material_yields else None
        }
        
        report_data['details'] = [
            {
                'material': material,
                'quotations': data['quotations'],
                'avg_yield': round(data['avg_yield'], 2),
                'min_yield': round(data['min_yield'], 2),
                'max_yield': round(data['max_yield'], 2)
            }
            for material, data in material_yields.items()
        ]
        
        return report_data

    def _generate_machine_utilization_report(self, quotations):
        """Generate machine utilization analysis"""
        report_data = {
            'title': 'Machine Utilization Report',
            'period': f'{self.date_from} to {self.date_to}',
            'summary': {},
            'details': []
        }
        
        # Machine usage statistics
        machine_usage = {}
        total_production_time = 0
        
        for quotation in quotations:
            if quotation.macchina_id and quotation.linear_length:
                machine = quotation.macchina_id.name
                
                # Calculate production time
                machine_speed = quotation.macchina_id.max_speed or 100
                efficiency = quotation.macchina_id.efficiency_factor or 0.85
                effective_speed = machine_speed * efficiency
                production_time = quotation.linear_length / (effective_speed * 60)  # hours
                
                if machine not in machine_usage:
                    machine_usage[machine] = {
                        'quotations': 0,
                        'total_time': 0,
                        'total_length': 0,
                        'total_cost': 0
                    }
                
                machine_usage[machine]['quotations'] += 1
                machine_usage[machine]['total_time'] += production_time
                machine_usage[machine]['total_length'] += quotation.linear_length
                machine_usage[machine]['total_cost'] += quotation.machine_cost
                total_production_time += production_time
        
        # Calculate utilization percentages
        days_in_period = (self.date_to - self.date_from).days + 1
        available_hours = days_in_period * 16  # Assume 16 hours per day operation
        
        for machine, data in machine_usage.items():
            data['utilization_percent'] = (data['total_time'] / available_hours) * 100 if available_hours else 0
            data['avg_time_per_job'] = data['total_time'] / data['quotations'] if data['quotations'] else 0
        
        report_data['summary'] = {
            'total_machines': len(machine_usage),
            'total_production_time': round(total_production_time, 2),
            'average_utilization': round(sum(data['utilization_percent'] for data in machine_usage.values()) / len(machine_usage), 2) if machine_usage else 0
        }
        
        report_data['details'] = [
            {
                'machine': machine,
                'quotations': data['quotations'],
                'total_time': round(data['total_time'], 2),
                'utilization_percent': round(data['utilization_percent'], 2),
                'total_length': round(data['total_length'], 2),
                'total_cost': round(data['total_cost'], 2)
            }
            for machine, data in machine_usage.items()
        ]
        
        return report_data

    def _generate_cost_analysis_report(self, quotations):
        """Generate cost analysis report"""
        report_data = {
            'title': 'Cost Analysis Report',
            'period': f'{self.date_from} to {self.date_to}',
            'summary': {},
            'details': []
        }
        
        total_cost = sum(q.total_cost for q in quotations)
        total_paper_cost = sum(q.paper_cost for q in quotations)
        total_die_cost = sum(q.die_cost for q in quotations)
        total_machine_cost = sum(q.machine_cost for q in quotations)
        
        # Cost breakdown by material
        material_costs = {}
        for quotation in quotations:
            if quotation.carta_id:
                material = quotation.carta_id.name
                if material not in material_costs:
                    material_costs[material] = {
                        'quotations': 0,
                        'total_cost': 0,
                        'paper_cost': 0,
                        'total_area': 0
                    }
                
                material_costs[material]['quotations'] += 1
                material_costs[material]['total_cost'] += quotation.total_cost
                material_costs[material]['paper_cost'] += quotation.paper_cost
                material_costs[material]['total_area'] += quotation.total_area_sqm
        
        # Calculate cost per square meter
        for material, data in material_costs.items():
            data['cost_per_sqm'] = data['paper_cost'] / data['total_area'] if data['total_area'] else 0
        
        report_data['summary'] = {
            'total_quotations': len(quotations),
            'total_cost': round(total_cost, 2),
            'paper_cost_percent': round((total_paper_cost / total_cost) * 100, 2) if total_cost else 0,
            'die_cost_percent': round((total_die_cost / total_cost) * 100, 2) if total_cost else 0,
            'machine_cost_percent': round((total_machine_cost / total_cost) * 100, 2) if total_cost else 0,
            'avg_cost_per_quotation': round(total_cost / len(quotations), 2) if quotations else 0
        }
        
        report_data['details'] = [
            {
                'material': material,
                'quotations': data['quotations'],
                'total_cost': round(data['total_cost'], 2),
                'paper_cost': round(data['paper_cost'], 2),
                'cost_per_sqm': round(data['cost_per_sqm'], 4),
                'total_area': round(data['total_area'], 2)
            }
            for material, data in material_costs.items()
        ]
        
        return report_data

    def _generate_die_usage_report(self, quotations):
        """Generate die usage analysis"""
        report_data = {
            'title': 'Die Usage Report',
            'period': f'{self.date_from} to {self.date_to}',
            'summary': {},
            'details': []
        }
        
        die_usage = {}
        for quotation in quotations:
            if quotation.fustella_id:
                die = quotation.fustella_id.name
                if die not in die_usage:
                    die_usage[die] = {
                        'quotations': 0,
                        'total_cost': 0,
                        'die_type': quotation.fustella_id.die_type,
                        'difficulty': getattr(quotation.fustella_id, 'stripping_difficulty', 'medium')
                    }
                
                die_usage[die]['quotations'] += 1
                die_usage[die]['total_cost'] += quotation.die_cost
        
        report_data['summary'] = {
            'total_dies_used': len(die_usage),
            'most_used_die': max(die_usage.items(), key=lambda x: x[1]['quotations'])[0] if die_usage else None,
            'total_die_costs': round(sum(data['total_cost'] for data in die_usage.values()), 2)
        }
        
        report_data['details'] = [
            {
                'die': die,
                'quotations': data['quotations'],
                'total_cost': round(data['total_cost'], 2),
                'die_type': data['die_type'],
                'difficulty': data['difficulty']
            }
            for die, data in die_usage.items()
        ]
        
        return report_data

    def _generate_material_consumption_report(self, quotations):
        """Generate material consumption analysis"""
        report_data = {
            'title': 'Material Consumption Report',
            'period': f'{self.date_from} to {self.date_to}',
            'summary': {},
            'details': []
        }
        
        material_consumption = {}
        total_area = 0
        
        for quotation in quotations:
            if quotation.carta_id and quotation.total_area_sqm:
                material = quotation.carta_id.name
                
                # Calculate actual consumption including waste
                waste_multiplier = 100.0 / quotation.yield_percentage if quotation.yield_percentage > 0 else 1.2
                actual_consumption = quotation.total_area_sqm * waste_multiplier
                
                if material not in material_consumption:
                    material_consumption[material] = {
                        'quotations': 0,
                        'theoretical_area': 0,
                        'actual_area': 0,
                        'total_cost': 0
                    }
                
                material_consumption[material]['quotations'] += 1
                material_consumption[material]['theoretical_area'] += quotation.total_area_sqm
                material_consumption[material]['actual_area'] += actual_consumption
                material_consumption[material]['total_cost'] += quotation.paper_cost
                total_area += actual_consumption
        
        # Calculate waste percentages
        for material, data in material_consumption.items():
            waste_area = data['actual_area'] - data['theoretical_area']
            data['waste_percent'] = (waste_area / data['theoretical_area']) * 100 if data['theoretical_area'] else 0
        
        report_data['summary'] = {
            'total_materials': len(material_consumption),
            'total_area_consumed': round(total_area, 2),
            'total_material_cost': round(sum(data['total_cost'] for data in material_consumption.values()), 2)
        }
        
        report_data['details'] = [
            {
                'material': material,
                'quotations': data['quotations'],
                'theoretical_area': round(data['theoretical_area'], 2),
                'actual_area': round(data['actual_area'], 2),
                'waste_percent': round(data['waste_percent'], 2),
                'total_cost': round(data['total_cost'], 2)
            }
            for material, data in material_consumption.items()
        ]
        
        return report_data

    def _convert_to_html(self, report_data):
        """Convert report data to HTML format"""
        if 'error' in report_data:
            return f'<p class="text-danger">{report_data["error"]}</p>'
        
        html = f'''
        <div class="production-report">
            <h2>{report_data['title']}</h2>
            <p><strong>Period:</strong> {report_data['period']}</p>
            
            <div class="report-summary">
                <h3>Summary</h3>
                <div class="row">
        '''
        
        # Add summary items
        for key, value in report_data['summary'].items():
            html += f'''
                    <div class="col-md-3">
                        <div class="card">
                            <div class="card-body">
                                <h5>{key.replace('_', ' ').title()}</h5>
                                <p class="card-text">{value}</p>
                            </div>
                        </div>
                    </div>
            '''
        
        html += '''
                </div>
            </div>
            
            <div class="report-details">
                <h3>Details</h3>
                <table class="table table-striped">
                    <thead>
                        <tr>
        '''
        
        # Add table headers
        if report_data['details']:
            for key in report_data['details'][0].keys():
                html += f'<th>{key.replace("_", " ").title()}</th>'
        
        html += '''
                        </tr>
                    </thead>
                    <tbody>
        '''
        
        # Add table rows
        for row in report_data['details']:
            html += '<tr>'
            for value in row.values():
                html += f'<td>{value}</td>'
            html += '</tr>'
        
        html += '''
                    </tbody>
                </table>
            </div>
        </div>
        '''
        
        return html

    def action_export_pdf(self):
        """Export report as PDF"""
        # This would integrate with Odoo's PDF generation
        # For now, return the HTML view
        return {
            'type': 'ir.actions.report',
            'report_name': 'label_quotation.production_analysis_report',
            'report_type': 'qweb-pdf',
            'data': {'report_data': self.report_data},
            'context': self.env.context,
        }


