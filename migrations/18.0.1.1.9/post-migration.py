# -*- coding: utf-8 -*-

import logging

_logger = logging.getLogger(__name__)


def migrate(env, version):
    """Migrate existing data to product-based system"""
    
    _logger.info("Starting migration to product-based label quotation system...")
    
    # Create product categories if they don't exist
    _create_product_categories(env)
    
    # Migrate existing materials to products
    _migrate_materials_to_products(env)
    
    # Migrate existing machines to products
    _migrate_machines_to_products(env)
    
    # Migrate existing dies to products
    _migrate_dies_to_products(env)
    
    _logger.info("Migration to product-based system completed successfully!")


def _create_product_categories(env):
    """Create product categories for label products"""
    
    _logger.info("Creating product categories...")
    
    # Get the main product category
    main_category = env.ref('product.product_category_all', raise_if_not_found=False)
    if not main_category:
        _logger.warning("Main product category not found, skipping category creation")
        return
    
    # Create label materials category
    materials_category = env['product.category'].search([
        ('name', '=', 'Label Materials')
    ], limit=1)
    
    if not materials_category:
        materials_category = env['product.category'].create({
            'name': 'Label Materials',
            'parent_id': main_category.id,
            'property_valuation': 'manual_periodic',
            'property_cost_method': 'standard',
        })
        _logger.info("Created Label Materials category")
    
    # Create label machines category
    machines_category = env['product.category'].search([
        ('name', '=', 'Label Machines')
    ], limit=1)
    
    if not machines_category:
        machines_category = env['product.category'].create({
            'name': 'Label Machines',
            'parent_id': main_category.id,
            'property_valuation': 'manual_periodic',
            'property_cost_method': 'standard',
        })
        _logger.info("Created Label Machines category")
    
    # Create label dies category
    dies_category = env['product.category'].search([
        ('name', '=', 'Label Dies')
    ], limit=1)
    
    if not dies_category:
        dies_category = env['product.category'].create({
            'name': 'Label Dies',
            'parent_id': main_category.id,
            'property_valuation': 'manual_periodic',
            'property_cost_method': 'standard',
        })
        _logger.info("Created Label Dies category")
    
    # Create label services category
    services_category = env['product.category'].search([
        ('name', '=', 'Label Services')
    ], limit=1)
    
    if not services_category:
        services_category = env['product.category'].create({
            'name': 'Label Services',
            'parent_id': main_category.id,
            'property_valuation': 'manual_periodic',
            'property_cost_method': 'standard',
        })
        _logger.info("Created Label Services category")


def _migrate_materials_to_products(env):
    """Migrate existing label.carta records to product.template"""
    
    _logger.info("Migrating materials to products...")
    
    materials_category = env['product.category'].search([
        ('name', '=', 'Label Materials')
    ], limit=1)
    
    if not materials_category:
        _logger.warning("Label Materials category not found, skipping material migration")
        return
    
    # Get all existing materials
    materials = env['label.carta'].search([])
    
    for material in materials:
        # Check if product already exists
        existing_product = env['product.template'].search([
            ('default_code', '=', material.code),
            ('is_label_material', '=', True)
        ], limit=1)
        
        if existing_product:
            _logger.info(f"Product for material {material.name} already exists, skipping")
            continue
        
        # Create product from material
        product_vals = {
            'name': material.name,
            'default_code': material.code or f"MAT_{material.id}",
            'categ_id': materials_category.id,
            'type': 'product',
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': material.cost_per_sqm or 0.0,
            'standard_price': (material.cost_per_sqm or 0.0) * 0.8,  # 20% margin
            'is_label_material': True,
            'paper_type': material.paper_type,
            'grammage': material.grammage,
            'thickness': material.thickness,
            'adhesive_type': material.adhesive_type,
            'adhesive_strength': material.adhesive_strength,
            'max_width': material.max_width,
            'max_length': material.max_length,
            'waste_factor': material.waste_factor,
            'minimum_order_quantity': material.minimum_order_quantity,
            'roll_width_standard': material.roll_width_standard,
            'roll_length_standard': material.roll_length_standard,
            'liner_type': material.liner_type,
            'liner_thickness': material.liner_thickness,
            'print_compatibility': material.print_compatibility,
            'temperature_range_min': material.temperature_range_min,
            'temperature_range_max': material.temperature_range_max,
            'shelf_life_months': material.shelf_life_months,
            'description': material.notes or f"Migrated from material {material.name}",
        }
        
        try:
            product = env['product.template'].create(product_vals)
            _logger.info(f"Created product for material: {material.name}")
        except Exception as e:
            _logger.error(f"Failed to create product for material {material.name}: {e}")


def _migrate_machines_to_products(env):
    """Migrate existing label.macchina records to product.template"""
    
    _logger.info("Migrating machines to products...")
    
    machines_category = env['product.category'].search([
        ('name', '=', 'Label Machines')
    ], limit=1)
    
    if not machines_category:
        _logger.warning("Label Machines category not found, skipping machine migration")
        return
    
    # Get all existing machines
    machines = env['label.macchina'].search([])
    
    for machine in machines:
        # Check if product already exists
        existing_product = env['product.template'].search([
            ('default_code', '=', machine.code),
            ('is_label_machine', '=', True)
        ], limit=1)
        
        if existing_product:
            _logger.info(f"Product for machine {machine.name} already exists, skipping")
            continue
        
        # Create product from machine
        product_vals = {
            'name': machine.name,
            'default_code': machine.code or f"MACH_{machine.id}",
            'categ_id': machines_category.id,
            'type': 'service',
            'sale_ok': True,
            'purchase_ok': False,
            'list_price': machine.production_cost_per_hour or 0.0,
            'standard_price': (machine.production_cost_per_hour or 0.0) * 0.8,
            'is_label_machine': True,
            'machine_type': machine.machine_type,
            'manufacturer': machine.manufacturer,
            'model': machine.model,
            'max_speed': machine.max_speed,
            'min_speed': machine.min_speed,
            'max_web_width': machine.max_web_width,
            'min_web_width': machine.min_web_width,
            'setup_time': machine.setup_time,
            'die_change_time': machine.die_change_time,
            'material_change_time': machine.material_change_time,
            'warm_up_time': machine.warm_up_time,
            'max_tracks': machine.max_tracks,
            'precision_rating': machine.precision_rating,
            'quality_factor': machine.quality_factor,
            'setup_cost_per_hour': machine.setup_cost_per_hour,
            'production_cost_per_hour': machine.production_cost_per_hour,
            'overhead_percentage': machine.overhead_percentage,
            'efficiency_factor': machine.efficiency_factor,
            'maintenance_cost_per_month': machine.maintenance_cost_per_month,
            'depreciation_cost_per_month': machine.depreciation_cost_per_month,
            'energy_cost_per_hour': machine.energy_cost_per_hour,
            'operator_cost_per_hour': machine.operator_cost_per_hour,
            'location': machine.location,
            'description': machine.notes or f"Migrated from machine {machine.name}",
        }
        
        try:
            product = env['product.template'].create(product_vals)
            _logger.info(f"Created product for machine: {machine.name}")
        except Exception as e:
            _logger.error(f"Failed to create product for machine {machine.name}: {e}")


def _migrate_dies_to_products(env):
    """Migrate existing label.fustella records to product.template"""
    
    _logger.info("Migrating dies to products...")
    
    dies_category = env['product.category'].search([
        ('name', '=', 'Label Dies')
    ], limit=1)
    
    if not dies_category:
        _logger.warning("Label Dies category not found, skipping die migration")
        return
    
    # Get all existing dies
    dies = env['label.fustella'].search([])
    
    for die in dies:
        # Check if product already exists
        existing_product = env['product.template'].search([
            ('default_code', '=', die.code),
            ('is_label_die', '=', True)
        ], limit=1)
        
        if existing_product:
            _logger.info(f"Product for die {die.name} already exists, skipping")
            continue
        
        # Create product from die
        product_vals = {
            'name': die.name,
            'default_code': die.code or f"DIE_{die.id}",
            'categ_id': dies_category.id,
            'type': 'service',
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': die.cost_per_use or 0.0,
            'standard_price': (die.cost_per_use or 0.0) * 0.8,
            'is_label_die': True,
            'die_type': die.die_type,
            'die_width': die.width,
            'die_length': die.length,
            'repeat_length': die.repeat_length,
            'die_max_tracks': die.max_tracks,
            'cutting_force_required': die.cutting_force_required,
            'stripping_difficulty': die.stripping_difficulty,
            'expected_lifetime_cuts': die.expected_lifetime_cuts,
            'current_usage_count': die.current_usage_count,
            'cost_per_use': die.cost_per_use,
            'setup_time_die': die.setup_time,
            'description': die.notes or f"Migrated from die {die.name}",
        }
        
        try:
            product = env['product.template'].create(product_vals)
            _logger.info(f"Created product for die: {die.name}")
        except Exception as e:
            _logger.error(f"Failed to create product for die {die.name}: {e}")
