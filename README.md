# Label Quotation System for Odoo 18

A comprehensive quotation system for blank label production with die-cutting calculations, designed specifically for labeling companies.

## Features

### Core Functionality
- **Paper Material Management**: Define different paper types (thermal, vellum, synthetic) with specifications, costs, and supplier information
- **Die Management**: Track dies with dimensions, costs, usage statistics, and special features
- **Machine Management**: Configure die-cutting machines (Vega+, Digicompact) with operational parameters and overhead costs
- **Label Quotation**: Create detailed quotations with automatic cost calculations

### Key Calculations
- **Material Yield**: Automatic calculation of material efficiency based on label dimensions and interspaces
- **Cost Breakdown**: Separate calculation of paper costs, die costs (amortized), and machine overhead
- **Linear Length**: Automatic calculation of total web length required
- **Pricing**: Configurable margin percentage with automatic selling price calculation

### Integration
- **Sales Orders**: Seamless integration with Odoo sales module
- **Product Creation**: Automatic product creation for accepted quotations
- **Customer Management**: Full integration with Odoo partner management

## Installation

1. Copy the `label_quotation` folder to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Label Quotation System" module

## Usage

### Setting Up Master Data

1. **Paper Materials**: Go to Label Quotation > Paper Materials and define your paper types
2. **Dies**: Go to Label Quotation > Dies and create your die specifications
3. **Machines**: Go to Label Quotation > Machines and configure your die-cutting machines

### Creating Quotations

1. Go to Label Quotation > Label Quotations
2. Click "Create" to start a new quotation
3. Fill in customer information and label specifications
4. Select appropriate paper material, die, and machine
5. Enter the total quantity of labels needed
6. Review the automatic cost calculations
7. Set your desired margin percentage
8. Send the quotation to the customer

### Processing Accepted Quotations

1. When a quotation is accepted, a sale order is automatically created
2. The system creates a product for the specific label configuration
3. Production can proceed with the detailed specifications

## Technical Details

### Models

- **label.carta**: Paper material specifications and costs
- **label.fustella**: Die specifications and amortized costs
- **label.macchina**: Machine configurations and operational costs
- **label.quotation**: Main quotation with automatic calculations

### Key Calculations

#### Material Yield
```
Yield % = (Label Area / Total Area per Label) × 100
Total Area per Label = (Label Width + Interspace) × (Label Height + Interspace)
```

#### Linear Length
```
Linear Length (m) = (Total Labels × Label Height + (Total Labels - 1) × Interspace) / 1000
```

#### Cost Breakdown
- **Paper Cost**: Total Area (m²) × Cost per m²
- **Die Cost**: Amortized Cost per Unit × Total Quantity
- **Machine Cost**: Setup Cost + (Production Time × Hourly Rate)

### Supported Machine Types

- **Vega+ (Prati)**: Up to 300 m/min, max 400mm web width
- **Digicompact (Prati)**: Up to 100 m/min, max 350mm web width

## Configuration

### User Groups
- **Label Quotation User**: Can create and manage quotations
- **Label Quotation Manager**: Full access including deletion

### Security
- Role-based access control
- Record-level security rules
- Integration with Odoo's standard security framework

## Support

For support and customization requests, please contact your Odoo implementation partner.

## License

LGPL-3
