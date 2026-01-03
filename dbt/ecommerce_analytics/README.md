# E-Commerce Analytics - dbt Project

## Overview

This dbt project transforms raw e-commerce data from the Olist Brazilian E-Commerce dataset into analytics-ready tables following dimensional modeling best practices.

## Project Structure

```
ecommerce_analytics/
├── models/
│   ├── staging/          # Clean, standardized views of raw data
│   │   ├── customers/
│   │   ├── orders/
│   │   ├── products/
│   │   └── sellers/
│   ├── intermediate/     # Business logic transformations
│   │   ├── customers/    # RFM segmentation, customer aggregations
│   │   ├── orders/       # Order enrichment, SLA calculations
│   │   ├── products/     # Product metrics
│   │   └── sellers/      # Seller performance
│   └── marts/            # Final analytics tables (star schema)
│       ├── customers/    # dim_customers, fct_customer_metrics
│       ├── orders/       # fct_orders, fct_order_items
│       ├── products/     # dim_products
│       └── sellers/      # dim_sellers
├── tests/                # Custom data quality tests
├── macros/               # Reusable SQL functions
├── seeds/                # Static reference data
└── snapshots/            # SCD Type 2 snapshots (if needed)
```

## Data Flow

```
Raw Data (raw schema)
  ↓
Staging Models (staging schema) - Clean & standardize
  ↓
Intermediate Models (intermediate schema) - Business logic
  ↓
Mart Models (marts schema) - Analytics-ready star schema
```

## Running dbt

### Development
```bash
cd dbt/ecommerce_analytics

# Test connection
dbt debug

# Run all models
dbt run

# Run specific model
dbt run --select stg_orders

# Test data quality
dbt test

# Generate documentation
dbt docs generate
dbt docs serve
```

### Useful Commands

```bash
# Full refresh (rebuild all tables)
dbt run --full-refresh

# Run models and tests
dbt build

# Run staging layer only
dbt run --select staging.*

# Run marts layer only
dbt run --select marts.*

# Test specific model
dbt test --select stg_orders
```

## Materialization Strategy

- **Staging**: `view` (low storage, always fresh)
- **Intermediate**: `view` (business logic, always fresh)
- **Marts**: `table` (fast queries, scheduled refreshes)

## Key Models

### Staging
- `stg_customers` - Cleaned customer data
- `stg_orders` - Cleaned order data with status
- `stg_order_items` - Order line items
- `stg_order_payments` - Payment transactions
- `stg_order_reviews` - Customer reviews
- `stg_products` - Product catalog
- `stg_sellers` - Seller information
- `stg_geolocation` - Geographic data

### Intermediate
- `int_customer_orders` - Customer order aggregations
- `int_rfm_scores` - RFM segmentation
- `int_order_enriched` - Orders with delivery SLA
- `int_product_performance` - Product metrics

### Marts
- `dim_customers` - Customer dimension
- `dim_products` - Product dimension
- `dim_sellers` - Seller dimension
- `dim_date` - Date dimension
- `fct_orders` - Order fact table
- `fct_order_items` - Order items fact table
- `fct_customer_metrics` - Customer lifetime value, churn risk

## Data Quality Tests

All models include:
- **Unique key tests**: Primary keys are unique
- **Not null tests**: Required fields have values
- **Referential integrity**: Foreign keys are valid
- **Business rules**: Custom validations (e.g., delivery date >= purchase date)

## Next Steps

1. Build staging models
2. Build intermediate models with RFM and SLA calculations
3. Build mart models (star schema)
4. Add comprehensive tests
5. Generate documentation
