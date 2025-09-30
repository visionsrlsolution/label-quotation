# Label Quotation Product Integration Guide

## Overview

The Label Quotation module now includes full integration with Odoo's product system, allowing you to manage materials, machines, and dies as standard Odoo products while maintaining all the specialized functionality for label production.

## Key Features

### 1. Product-Based Materials
- **Thermal Papers**: FSC certified thermal papers with hot melt adhesive
- **Vellum Papers**: High-quality vellum papers for various applications
- **Material Properties**: Grammage, thickness, adhesive type, temperature ranges
- **Production Settings**: Waste factors, minimum order quantities, roll dimensions

### 2. Product-Based Machines
- **Vega Plus LF450**: High-speed die-cutting machine for labels up to 400mm width
- **Digicompact**: Compact die-cutting machine for smaller label formats
- **Machine Specifications**: Speed, web width, precision ratings, efficiency factors
- **Cost Modeling**: Setup costs, production costs, maintenance, depreciation

### 3. Product-Based Dies
- **Rectangular Dies**: Standard rectangular dies for various label sizes
- **Shaped Dies**: Oval, round, and custom-shaped dies
- **Kiss Cut Dies**: Specialized dies for kiss-cut applications
- **Usage Tracking**: Lifetime tracking, depreciation, setup times

## Installation and Setup

### 1. Install the Module
```bash
# Copy the module to your Odoo addons directory
# Update the module list and install
```

### 2. Product Categories
The system automatically creates the following product categories:
- **Label Materials**: For paper materials and substrates
- **Label Machines**: For production equipment
- **Label Dies**: For cutting tools and dies
- **Label Services**: For quotation and production services

### 3. Pre-configured Products
The module includes pre-configured products based on industry standards:

#### Materials
- Thermal FSC (CATEA02)
- Thermal ECO BPA FREE FSC (THERMAL_ECO)
- Vellum Neutro FSC (CAVA03)
- Vellum HERMA white (HERMA_601)

#### Machines
- Prati Vega Plus LF450 (VEGA_LF450)
- Prati Digicompact (DIGICOMPACT)

#### Dies
- Rectangle 50x30mm (RECT_50_30)
- Rectangle 100x60mm (RECT_100_60)
- Oval 60x40mm (OVAL_60_40)
- Round Ø50mm (ROUND_D50)
- Bottle Shape 80x120mm (BOTTLE_80_120)
- Kiss Cut Rectangle 80x50mm (KISS_RECT_80_50)

## Usage

### 1. Creating Label Quotations with Products

#### Using the Product Integration
1. Navigate to **Label Quotation → Quotations (Product Integration)**
2. Create a new quotation
3. Select products from the dropdown menus:
   - **Material Product**: Choose from available label materials
   - **Machine Product**: Select the production machine
   - **Die Product**: Pick the appropriate die
4. Enter label specifications (dimensions, quantity, etc.)
5. The system automatically calculates costs and production parameters

#### Legacy Mode
- The original quotation system remains available for backward compatibility
- Navigate to **Label Quotation → Quotations** for the legacy interface

### 2. Managing Products

#### Adding New Materials
1. Go to **Label Quotation → Label Materials**
2. Create a new product
3. Set `Is Label Material` to True
4. Configure material properties:
   - Paper type, grammage, thickness
   - Adhesive specifications
   - Production parameters
   - Technical specifications

#### Adding New Machines
1. Go to **Label Quotation → Label Machines**
2. Create a new product
3. Set `Is Label Machine` to True
4. Configure machine properties:
   - Machine type, manufacturer, model
   - Performance specifications
   - Cost parameters
   - Capabilities and limitations

#### Adding New Dies
1. Go to **Label Quotation → Label Dies**
2. Create a new product
3. Set `Is Label Die` to True
4. Configure die properties:
   - Die type, dimensions
   - Cutting specifications
   - Usage tracking parameters
   - Cost and setup information

### 3. Product Views and Forms

#### Material Product Form
- **Basic Properties**: Paper type, grammage, thickness, adhesive
- **Dimensions**: Max width/length, standard roll dimensions
- **Production Settings**: Waste factors, minimum order quantities
- **Technical Specifications**: Print compatibility, temperature ranges

#### Machine Product Form
- **Basic Properties**: Machine type, manufacturer, model, location
- **Performance**: Speed ranges, web width capabilities
- **Setup Times**: Setup, die change, material change, warm-up times
- **Capabilities**: Max tracks, precision rating, quality factor
- **Costs**: Setup costs, production costs, operating costs

#### Die Product Form
- **Basic Properties**: Die type, dimensions, repeat length
- **Capabilities**: Max tracks, cutting force, stripping difficulty
- **Usage Tracking**: Expected lifetime, current usage, depreciation
- **Setup**: Setup time and cost information

## Integration Benefits

### 1. Standard Odoo Integration
- **Inventory Management**: Track material stock levels
- **Purchase Orders**: Order materials through standard Odoo processes
- **Sales Orders**: Convert quotations to sales orders with products
- **Accounting**: Automatic cost tracking and margin calculations

### 2. Advanced Cost Modeling
- **Material Costs**: Based on actual product prices and waste factors
- **Machine Costs**: Including setup, production, and overhead costs
- **Die Costs**: Usage-based depreciation and setup costs
- **Total Cost Calculation**: Comprehensive cost modeling

### 3. Production Optimization
- **Automatic Calculations**: Web width, production time, material usage
- **Constraint Validation**: Ensures feasible production configurations
- **Yield Optimization**: Maximizes material utilization
- **Cost Optimization**: Finds the most cost-effective configuration

## Migration from Legacy System

### Automatic Migration
The system includes an automatic migration script that:
1. Creates product categories
2. Migrates existing materials to products
3. Migrates existing machines to products
4. Migrates existing dies to products
5. Preserves all existing data and relationships

### Manual Migration
If you prefer manual migration:
1. Export data from legacy models
2. Create corresponding products
3. Map relationships between old and new records
4. Update quotations to use new product references

## Best Practices

### 1. Product Management
- **Regular Updates**: Keep product specifications current
- **Cost Reviews**: Regularly review and update cost parameters
- **Supplier Integration**: Link products to suppliers for procurement
- **Quality Control**: Monitor product performance and quality factors

### 2. Quotation Process
- **Product Selection**: Choose appropriate products for each quotation
- **Validation**: Use the system's validation features
- **Cost Analysis**: Review calculated costs before finalizing
- **Documentation**: Maintain detailed records of specifications

### 3. Production Planning
- **Capacity Planning**: Consider machine availability and capacity
- **Material Planning**: Ensure adequate material stock
- **Die Management**: Track die usage and maintenance
- **Quality Assurance**: Monitor production quality and yields

## Troubleshooting

### Common Issues

#### Product Not Available in Dropdown
- Check that the product has the correct type flag set
- Verify the product is active
- Ensure proper product category assignment

#### Cost Calculations Incorrect
- Review product cost parameters
- Check material waste factors
- Verify machine efficiency factors
- Validate die usage parameters

#### Migration Issues
- Check migration logs for errors
- Verify data integrity before migration
- Test migration on a copy of the database first
- Contact support if issues persist

### Performance Optimization
- **Database Maintenance**: Regular database optimization
- **Product Caching**: Use product caching for large catalogs
- **Report Optimization**: Optimize report generation for large datasets
- **Archive Old Data**: Archive old quotations and products

## Support and Maintenance

### Regular Maintenance
- **Data Backup**: Regular backups of product and quotation data
- **Performance Monitoring**: Monitor system performance
- **Update Management**: Keep the module updated
- **User Training**: Regular training on new features

### Support Resources
- **Documentation**: Comprehensive documentation and guides
- **Community Support**: User community and forums
- **Professional Support**: Available for enterprise customers
- **Training Services**: Custom training and implementation services

## Conclusion

The product integration system provides a powerful and flexible foundation for label quotation management while maintaining full compatibility with Odoo's standard product management capabilities. This integration enables better inventory management, cost tracking, and production planning while preserving all the specialized functionality required for label manufacturing.

For additional support or questions, please refer to the module documentation or contact your system administrator.
