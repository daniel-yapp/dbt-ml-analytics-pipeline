# Getting Started with dbt E-Commerce Analytics

## Quick Start

### 1. Prerequisites

Make sure you've completed the initial setup from the main README:
- Python 3.11+ with virtual environment activated
- DuckDB database (`ecommerce_raw.duckdb`) exists in project root
- Raw data loaded into DuckDB

### 2. Navigate to dbt project

```bash
cd dbt/ecommerce_analytics
```

### 3. Verify connection

```bash
# Test connection to DuckDB
dbt debug --profiles-dir ..

# Expected output: "All checks passed!"
```

### 4. Run dbt models

```bash
# Run all models (staging → intermediate → marts)
dbt run --profiles-dir ..

# Expected: 17 models built successfully
```

### 5. Test data quality

```bash
# Run all tests
dbt test --profiles-dir ..

# Expected: All tests passed
```

### 6. Generate documentation

```bash
# Generate docs
dbt docs generate --profiles-dir ..

# Serve docs locally (opens browser)
dbt docs serve --profiles-dir ..
```

## What Just Happened?

After running `dbt run`, your DuckDB database now contains:

### Staging Schema (8 views)
Clean, standardized versions of raw data:
- `staging.stg_customers`
- `staging.stg_orders`
- `staging.stg_order_items`
- `staging.stg_order_payments`
- `staging.stg_order_reviews`
- `staging.stg_products`
- `staging.stg_sellers`
- `staging.stg_geolocation`

### Intermediate Schema (4 views)
Business logic transformations:
- `intermediate.int_customer_orders` - Customer aggregations
- `intermediate.int_rfm_scores` - RFM segmentation
- `intermediate.int_product_performance` - Product metrics
- `intermediate.int_seller_performance` - Seller metrics

### Marts Schema (5 tables)
Analytics-ready star schema:
- `marts.dim_customers` - Customer dimension (with RFM)
- `marts.dim_products` - Product dimension
- `marts.dim_sellers` - Seller dimension
- `marts.fct_orders` - Order fact table
- `marts.fct_order_items` - Order items fact table

## Querying the Data

Connect to DuckDB and query the marts:

```bash
duckdb ../../ecommerce_raw.duckdb
```

```sql
-- Top 10 customers by revenue
SELECT
    customer_key,
    customer_segment,
    total_revenue,
    avg_order_value,
    total_orders
FROM marts.dim_customers
ORDER BY total_revenue DESC
LIMIT 10;

-- RFM segment distribution
SELECT
    customer_segment,
    COUNT(*) as customer_count,
    SUM(total_revenue) as segment_revenue
FROM marts.dim_customers
GROUP BY customer_segment
ORDER BY segment_revenue DESC;

-- Top selling products
SELECT
    p.product_key,
    p.category_english,
    p.total_revenue,
    p.total_items_sold,
    p.avg_review_score
FROM marts.dim_products p
ORDER BY p.total_revenue DESC
LIMIT 10;

-- Monthly order trends
SELECT
    DATE_TRUNC('month', purchased_at) as month,
    COUNT(*) as orders,
    SUM(order_value) as revenue,
    AVG(order_value) as avg_order_value
FROM marts.fct_orders
WHERE is_delivered = true
GROUP BY 1
ORDER BY 1;
```

## Common dbt Commands

```bash
# Run specific model
dbt run --select stg_orders --profiles-dir ..

# Run model and all downstream dependencies
dbt run --select stg_orders+ --profiles-dir ..

# Run staging layer only
dbt run --select staging.* --profiles-dir ..

# Run marts layer only
dbt run --select marts.* --profiles-dir ..

# Full refresh (rebuild tables from scratch)
dbt run --full-refresh --profiles-dir ..

# Run and test
dbt build --profiles-dir ..

# Test specific model
dbt test --select fct_orders --profiles-dir ..

# Compile SQL without running
dbt compile --profiles-dir ..
```

## Troubleshooting

### "Database not found"
Make sure `ecommerce_raw.duckdb` exists in the project root:
```bash
ls ../../ecommerce_raw.duckdb
```

### "Relation does not exist"
Run the data loading script first:
```bash
python ../../scripts/load_raw_data.py
```

### "No module named 'dbt'"
Activate virtual environment:
```bash
source ../../.venv/Scripts/activate  # Windows
source ../../.venv/bin/activate     # Mac/Linux
```

## Next Steps

1. **Explore the lineage graph**: Run `dbt docs serve` and click "View Lineage Graph"
2. **Add custom business metrics**: Create new models in `models/marts/`
3. **Schedule refreshes**: Set up dbt Cloud or Airflow to run `dbt run` daily
4. **Build dashboards**: Connect Streamlit or Power BI to the marts schema

## File Structure Reference

```
dbt/ecommerce_analytics/
├── dbt_project.yml        # Project configuration
├── models/
│   ├── staging/
│   │   ├── schema.yml     # Source and staging tests
│   │   └── stg_*.sql      # 8 staging models
│   ├── intermediate/
│   │   ├── schema.yml     # Intermediate tests
│   │   └── int_*.sql      # 4 intermediate models
│   └── marts/
│       ├── schema.yml     # Mart tests
│       ├── dim_*.sql      # 3 dimension tables
│       └── fct_*.sql      # 2 fact tables
└── ../profiles.yml        # Database connection config
```

## Performance Tips

- **Staging/Intermediate**: Views (always fresh, minimal storage)
- **Marts**: Tables (fast queries, refresh as needed)
- For production: Schedule `dbt run` to refresh marts daily or hourly
- Use `--select` to run only what changed: `dbt run --select state:modified+`
