# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductionOptimizationWizard(models.TransientModel):
    _name = 'production.optimization.wizard'
    _description = 'Production Parameters Optimization Wizard'

    # Input parameters
    label_width = fields.Float(
        string='Label Width (mm)',
        required=True,
        help='Width of individual labels in millimeters'
    )
    
    label_height = fields.Float(
        string='Label Height (mm)',
        required=True,
        help='Height of individual labels in millimeters'
    )
    
    total_quantity = fields.Integer(
        string='Total Quantity',
        required=True,
        help='Total number of labels to produce'
    )
    
    carta_id = fields.Many2one(
        'label.carta',
        string='Paper Material',
        required=True
    )
    
    available_machines = fields.Many2many(
        'label.macchina',
        string='Available Machines',
        help='Machines available for this production'
    )
    
    available_dies = fields.Many2many(
        'label.fustella',
        string='Available Dies',
        help='Dies available for this production'
    )
    
    # Optimization criteria
    optimization_priority = fields.Selection([
        ('cost', 'Minimize Cost'),
        ('time', 'Minimize Production Time'),
        ('yield', 'Maximize Material Yield'),
        ('quality', 'Maximize Quality'),
    ], string='Optimization Priority', default='cost', required=True)
    
    max_tracks_preference = fields.Integer(
        string='Maximum Tracks Preference',
        default=4,
        help='Preferred maximum number of tracks'
    )
    
    interspace_preference = fields.Float(
        string='Interspace Preference (mm)',
        default=3.2,
        help='Preferred interspace between labels'
    )
    
    # Results
    optimization_results = fields.Text(
        string='Optimization Results',
        readonly=True
    )
    
    recommended_machine_id = fields.Many2one(
        'label.macchina',
        string='Recommended Machine',
        readonly=True
    )
    
    recommended_die_id = fields.Many2one(
        'label.fustella',
        string='Recommended Die',
        readonly=True
    )
    
    recommended_tracks = fields.Integer(
        string='Recommended Tracks',
        readonly=True
    )
    
    recommended_interspace = fields.Float(
        string='Recommended Interspace (mm)',
        readonly=True
    )
    
    estimated_cost = fields.Float(
        string='Estimated Cost (€)',
        readonly=True
    )
    
    estimated_yield = fields.Float(
        string='Estimated Yield (%)',
        readonly=True
    )
    
    estimated_production_time = fields.Float(
        string='Estimated Production Time (hours)',
        readonly=True
    )

    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)
        
        # Get quotation from context if available
        quotation_id = self.env.context.get('active_id')
        if quotation_id and self.env.context.get('active_model') == 'label.quotation':
            quotation = self.env['label.quotation'].browse(quotation_id)
            if quotation.exists():
                res.update({
                    'label_width': quotation.label_width,
                    'label_height': quotation.label_height,
                    'total_quantity': quotation.total_quantity,
                    'carta_id': quotation.carta_id.id if quotation.carta_id else False,
                })
        
        # Set default available machines and dies
        res['available_machines'] = [(6, 0, self.env['label.macchina'].search([('active', '=', True)]).ids)]
        res['available_dies'] = [(6, 0, self.env['label.fustella'].search([('active', '=', True)]).ids)]
        
        return res

    def action_optimize(self):
        """Run optimization algorithm"""
        self.ensure_one()
        
        if not self.label_width or not self.label_height or not self.total_quantity:
            raise ValidationError(_('Please provide all required measurements.'))
        
        best_solution = self._find_optimal_configuration()
        
        # Update wizard with results
        self.write({
            'recommended_machine_id': best_solution['machine_id'],
            'recommended_die_id': best_solution['die_id'],
            'recommended_tracks': best_solution['tracks'],
            'recommended_interspace': best_solution['interspace'],
            'estimated_cost': best_solution['cost'],
            'estimated_yield': best_solution['yield'],
            'estimated_production_time': best_solution['production_time'],
            'optimization_results': best_solution['description']
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'production.optimization.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }

    def _find_optimal_configuration(self):
        """Find the optimal production configuration"""
        self.ensure_one()
        
        best_score = float('inf') if self.optimization_priority == 'cost' else 0
        best_solution = None
        
        # Test different configurations
        for machine in self.available_machines:
            for die in self.available_dies:
                for tracks in range(1, min(self.max_tracks_preference + 1, 
                                         machine.max_tracks or 10,
                                         die.max_tracks or 10)):
                    for interspace in [2.0, 3.2, 4.0, 5.0]:  # Test common interspace values
                        
                        solution = self._evaluate_configuration(machine, die, tracks, interspace)
                        
                        if solution['feasible']:
                            score = self._calculate_score(solution)
                            
                            if self.optimization_priority == 'cost':
                                if score < best_score:
                                    best_score = score
                                    best_solution = solution
                            else:  # For other criteria (maximize)
                                if score > best_score:
                                    best_score = score
                                    best_solution = solution
        
        if not best_solution:
            return {
                'machine_id': False,
                'die_id': False,
                'tracks': 1,
                'interspace': 3.2,
                'cost': 0,
                'yield': 0,
                'production_time': 0,
                'description': _('No feasible configuration found with the given constraints.')
            }
        
        return best_solution

    def _evaluate_configuration(self, machine, die, tracks, interspace):
        """Evaluate a specific configuration"""
        
        # Check basic feasibility
        edge_margin = 5.0
        web_width = (self.label_width * tracks) + (interspace * (tracks - 1)) + (2 * edge_margin)
        
        feasible = True
        
        # Check material width constraint
        if web_width > self.carta_id.max_width:
            feasible = False
        
        # Check machine width constraint
        if web_width > machine.max_web_width:
            feasible = False
        
        if not feasible:
            return {'feasible': False}
        
        # Calculate production parameters
        labels_per_meter = 1000 / (self.label_height + interspace)
        total_labels_per_meter = labels_per_meter * tracks
        linear_length = self.total_quantity / total_labels_per_meter
        
        # Calculate yield
        yield_percentage = self._calculate_yield(web_width, linear_length, tracks, die)
        
        # Calculate costs
        costs = self._calculate_costs(machine, die, linear_length, yield_percentage)
        
        # Calculate production time
        production_time = self._calculate_production_time(machine, linear_length)
        
        return {
            'feasible': True,
            'machine_id': machine.id,
            'die_id': die.id,
            'tracks': tracks,
            'interspace': interspace,
            'web_width': web_width,
            'linear_length': linear_length,
            'yield': yield_percentage,
            'cost': costs['total'],
            'production_time': production_time,
            'description': self._generate_description(machine, die, tracks, interspace, yield_percentage, costs, production_time)
        }

    def _calculate_yield(self, web_width, linear_length, tracks, die):
        """Calculate material yield for this configuration"""
        base_yield = 95.0
        
        # Material waste factor
        if hasattr(self.carta_id, 'waste_factor'):
            base_yield -= (self.carta_id.waste_factor or 5.0)
        
        # Width efficiency
        width_efficiency = web_width / self.carta_id.max_width
        if width_efficiency < 0.6:
            base_yield -= 10
        elif width_efficiency < 0.8:
            base_yield -= 5
        
        # Die difficulty
        if hasattr(die, 'stripping_difficulty'):
            penalties = {'easy': 0, 'medium': 2, 'difficult': 5, 'very_difficult': 10}
            base_yield -= penalties.get(die.stripping_difficulty, 2)
        
        # Small run penalty
        if linear_length < 100:
            base_yield -= 5
        elif linear_length < 500:
            base_yield -= 2
        
        # Track optimization
        if tracks == 1:
            base_yield -= 3
        elif tracks >= 4:
            base_yield += 2
        
        return max(0, min(100, base_yield))

    def _calculate_costs(self, machine, die, linear_length, yield_percentage):
        """Calculate costs for this configuration"""
        
        # Material cost
        label_area_sqm = (self.label_width * self.label_height) / 1000000
        total_area_sqm = label_area_sqm * self.total_quantity
        
        waste_multiplier = 100.0 / yield_percentage if yield_percentage > 0 else 1.5
        actual_material_area = total_area_sqm * waste_multiplier
        material_cost = actual_material_area * self.carta_id.cost_per_sqm
        
        # Die cost
        die_cost = die.cost_per_use or 0
        if hasattr(die, 'depreciation_per_use'):
            die_cost += die.depreciation_per_use or 0
        
        # Machine cost
        machine_speed = machine.max_speed or 100
        efficiency = machine.efficiency_factor or 0.85
        effective_speed = machine_speed * efficiency
        
        production_time_hours = linear_length / (effective_speed * 60)
        setup_time_hours = (machine.setup_time or 30) / 60
        
        total_time = production_time_hours + setup_time_hours
        
        setup_cost = setup_time_hours * (machine.setup_cost_per_hour or 0)
        production_cost = production_time_hours * (machine.production_cost_per_hour or 0)
        energy_cost = total_time * (machine.energy_cost_per_hour or 0)
        operator_cost = total_time * (machine.operator_cost_per_hour or 0)
        
        base_machine_cost = setup_cost + production_cost + energy_cost + operator_cost
        overhead_multiplier = 1 + (machine.overhead_percentage or 0) / 100
        machine_cost = base_machine_cost * overhead_multiplier
        
        return {
            'material': material_cost,
            'die': die_cost,
            'machine': machine_cost,
            'total': material_cost + die_cost + machine_cost
        }

    def _calculate_production_time(self, machine, linear_length):
        """Calculate total production time"""
        machine_speed = machine.max_speed or 100
        efficiency = machine.efficiency_factor or 0.85
        effective_speed = machine_speed * efficiency
        
        production_time_hours = linear_length / (effective_speed * 60)
        setup_time_hours = (machine.setup_time or 30) / 60
        
        return production_time_hours + setup_time_hours

    def _calculate_score(self, solution):
        """Calculate optimization score based on priority"""
        if self.optimization_priority == 'cost':
            return solution['cost']
        elif self.optimization_priority == 'time':
            return -solution['production_time']  # Negative for minimization
        elif self.optimization_priority == 'yield':
            return solution['yield']
        elif self.optimization_priority == 'quality':
            # Combine multiple quality factors
            quality_score = solution['yield']
            if solution.get('tracks', 1) > 1:
                quality_score += 5  # Multi-track bonus
            return quality_score
        return 0

    def _generate_description(self, machine, die, tracks, interspace, yield_percentage, costs, production_time):
        """Generate human-readable description of the solution"""
        description = _("""
Recommended Configuration:
• Machine: {machine}
• Die: {die}
• Tracks: {tracks}
• Interspace: {interspace:.1f}mm
• Expected Yield: {yield_pct:.1f}%
• Total Cost: €{cost:.2f}
• Production Time: {time:.2f} hours

Cost Breakdown:
• Material: €{material:.2f}
• Die: €{die_cost:.2f}
• Machine: €{machine_cost:.2f}
        """).format(
            machine=machine.name,
            die=die.name,
            tracks=tracks,
            interspace=interspace,
            yield_pct=yield_percentage,
            cost=costs['total'],
            time=production_time,
            material=costs['material'],
            die_cost=costs['die'],
            machine_cost=costs['machine']
        )
        
        return description

    def action_apply_to_quotation(self):
        """Apply recommended configuration to the quotation"""
        self.ensure_one()
        
        quotation_id = self.env.context.get('active_id')
        if quotation_id and self.env.context.get('active_model') == 'label.quotation':
            quotation = self.env['label.quotation'].browse(quotation_id)
            if quotation.exists():
                quotation.write({
                    'macchina_id': self.recommended_machine_id.id,
                    'fustella_id': self.recommended_die_id.id,
                    'tracks': self.recommended_tracks,
                    'interspace': self.recommended_interspace,
                })
                
                return {
                    'type': 'ir.actions.act_window_close',
                }
        
        raise ValidationError(_('Cannot apply configuration: no active quotation found.'))

    def action_create_quotation(self):
        """Create new quotation with recommended configuration"""
        self.ensure_one()
        
        quotation_vals = {
            'label_width': self.label_width,
            'label_height': self.label_height,
            'total_quantity': self.total_quantity,
            'carta_id': self.carta_id.id,
            'macchina_id': self.recommended_machine_id.id,
            'fustella_id': self.recommended_die_id.id,
            'tracks': self.recommended_tracks,
            'interspace': self.recommended_interspace,
        }
        
        quotation = self.env['label.quotation'].create(quotation_vals)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'label.quotation',
            'res_id': quotation.id,
            'view_mode': 'form',
            'target': 'current',
        }
