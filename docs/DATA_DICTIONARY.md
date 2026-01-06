# Data Dictionary

## Olist Brazilian E-Commerce Dataset

This document describes all tables and columns in the Olist dataset.

---

## Table Relationships

```
customers ─┐
           ├─> orders ─┬─> order_items ─> products
           │           ├─> order_payments
           │           └─> order_reviews
sellers ───┘

geolocation (lookup table for zip codes)
```

---

## Tables

### 1. olist_customers_dataset

Customer information (anonymized).

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| customer_id | VARCHAR | Unique customer identifier | Primary key |
| customer_unique_id | VARCHAR | Unique customer identifier across all orders | One customer can have multiple customer_ids |
| customer_zip_code_prefix | INTEGER | First 5 digits of zip code | Join with geolocation |
| customer_city | VARCHAR | Customer city name | |
| customer_state | VARCHAR | Customer state (2-letter code) | |

**Sample Row Count**: ~99,441

---

### 2. olist_orders_dataset

Order information.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| order_id | VARCHAR | Unique order identifier | Primary key |
| customer_id | VARCHAR | Customer who made the order | Foreign key to customers |
| order_status | VARCHAR | Order status | delivered, shipped, canceled, etc. |
| order_purchase_timestamp | TIMESTAMP | Purchase timestamp | |
| order_approved_at | TIMESTAMP | Payment approval timestamp | Can be null |
| order_delivered_carrier_date | TIMESTAMP | Order handoff to carrier | Can be null |
| order_delivered_customer_date | TIMESTAMP | Actual delivery date | Can be null |
| order_estimated_delivery_date | TIMESTAMP | Estimated delivery date | |

**Sample Row Count**: ~99,441

**Order Status Values**:
- delivered
- shipped
- canceled
- unavailable
- invoiced
- processing
- created
- approved

---

### 3. olist_order_items_dataset

Items within each order.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| order_id | VARCHAR | Order identifier | Foreign key to orders |
| order_item_id | INTEGER | Sequential number identifying item within order | Starts at 1 |
| product_id | VARCHAR | Product identifier | Foreign key to products |
| seller_id | VARCHAR | Seller identifier | Foreign key to sellers |
| shipping_limit_date | TIMESTAMP | Seller shipping limit date | |
| price | DOUBLE | Item price | |
| freight_value | DOUBLE | Freight/shipping cost | |

**Sample Row Count**: ~112,650
**Primary Key**: (order_id, order_item_id)

---

### 4. olist_order_payments_dataset

Payment information for orders.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| order_id | VARCHAR | Order identifier | Foreign key to orders |
| payment_sequential | INTEGER | Sequential number for split payments | |
| payment_type | VARCHAR | Payment method | credit_card, boleto, voucher, debit_card |
| payment_installments | INTEGER | Number of installments | |
| payment_value | DOUBLE | Payment amount | |

**Sample Row Count**: ~103,886

**Payment Types**:
- credit_card
- boleto (Brazilian instant payment method)
- voucher
- debit_card

---

### 5. olist_order_reviews_dataset

Customer reviews and ratings.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| review_id | VARCHAR | Unique review identifier | Primary key |
| order_id | VARCHAR | Order identifier | Foreign key to orders |
| review_score | INTEGER | Rating (1-5 stars) | |
| review_comment_title | VARCHAR | Review title | Can be null |
| review_comment_message | VARCHAR | Review comment text | Can be null, Portuguese |
| review_creation_date | TIMESTAMP | Review creation timestamp | |
| review_answer_timestamp | TIMESTAMP | Review answer timestamp | Can be null |

**Sample Row Count**: ~99,224

---

### 6. olist_products_dataset

Product information.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| product_id | VARCHAR | Unique product identifier | Primary key |
| product_category_name | VARCHAR | Product category | In Portuguese, can be null |
| product_name_lenght | INTEGER | Product name character count | Can be null |
| product_description_lenght | INTEGER | Description character count | Can be null |
| product_photos_qty | INTEGER | Number of product photos | Can be null |
| product_weight_g | INTEGER | Product weight in grams | Can be null |
| product_length_cm | INTEGER | Product length in cm | Can be null |
| product_height_cm | INTEGER | Product height in cm | Can be null |
| product_width_cm | INTEGER | Product width in cm | Can be null |

**Sample Row Count**: ~32,951

**Note**: Product category names are in Portuguese and need translation in staging layer.

---

### 7. olist_sellers_dataset

Seller information.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| seller_id | VARCHAR | Unique seller identifier | Primary key |
| seller_zip_code_prefix | INTEGER | First 5 digits of seller zip code | Join with geolocation |
| seller_city | VARCHAR | Seller city name | |
| seller_state | VARCHAR | Seller state (2-letter code) | |

**Sample Row Count**: ~3,095

---

### 8. olist_geolocation_dataset

Brazilian zip code and lat/lng coordinates.

| Column | Type | Description | Notes |
|--------|------|-------------|-------|
| geolocation_zip_code_prefix | INTEGER | First 5 digits of zip code | |
| geolocation_lat | DOUBLE | Latitude | |
| geolocation_lng | DOUBLE | Longitude | |
| geolocation_city | VARCHAR | City name | |
| geolocation_state | VARCHAR | State (2-letter code) | |

**Sample Row Count**: ~1,000,493

**Note**: Multiple lat/lng coordinates per zip code prefix. Will need aggregation.

---

## Business Metrics

### Key Performance Indicators (KPIs)

| Metric | Formula | Description |
|--------|---------|-------------|
| GMV (Gross Merchandise Value) | SUM(price + freight_value) | Total order value |
| Average Order Value (AOV) | GMV / COUNT(DISTINCT orders) | Average revenue per order |
| Customer Lifetime Value (CLV) | TBD - ML Model | Predicted customer value |
| Churn Rate | TBD | Customers who haven't ordered in 90 days |
| Delivery SLA % | Delivered before estimate / Total delivered | On-time delivery rate |
| Review Score Average | AVG(review_score) | Customer satisfaction |

### RFM Metrics

| Metric | Description |
|--------|-------------|
| Recency | Days since last order |
| Frequency | Number of orders |
| Monetary | Total spending |

---

## Data Quality Notes

**To be filled after EDA:**
- Missing value patterns
- Outliers and anomalies
- Data inconsistencies
- Duplicate records
- Referential integrity issues

---

## Next Steps

1. Complete EDA to fill in data quality notes
2. Document transformation logic in dbt models
3. Create metrics layer documentation
