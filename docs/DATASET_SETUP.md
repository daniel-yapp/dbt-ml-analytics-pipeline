# Dataset Setup Guide

## Olist Brazilian E-Commerce Dataset

This project uses the **Olist Brazilian E-Commerce** dataset from Kaggle, which contains real commercial data from 100,000+ orders made at the Olist Store.

### Dataset Overview

- **Source**: [Kaggle - Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Size**: ~300 MB (8 CSV files)
- **Records**: 100,000+ orders, 100,000+ reviews
- **Time Period**: 2016-2018

### Tables Included

1. `olist_customers_dataset.csv` - Customer information
2. `olist_geolocation_dataset.csv` - Brazilian zip codes and coordinates
3. `olist_order_items_dataset.csv` - Items within each order
4. `olist_order_payments_dataset.csv` - Payment information
5. `olist_order_reviews_dataset.csv` - Customer reviews
6. `olist_orders_dataset.csv` - Order information
7. `olist_products_dataset.csv` - Product information
8. `olist_sellers_dataset.csv` - Seller information

## Setup Instructions

### Step 1: Create Kaggle Account

1. Go to [kaggle.com](https://www.kaggle.com)
2. Sign up for a free account (if you don't have one)

### Step 2: Download Dataset Manually

1. Visit: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
2. Click the **"Download"** button (may need to accept terms)
3. Extract the downloaded zip file
4. Move all 8 CSV files to the `data/raw/` directory in this project

### Step 3: Verify Dataset

After downloading, verify that you have all 8 CSV files:

```bash
ls data/raw/
```

Expected output:
```
olist_customers_dataset.csv
olist_geolocation_dataset.csv
olist_order_items_dataset.csv
olist_order_payments_dataset.csv
olist_order_reviews_dataset.csv
olist_orders_dataset.csv
olist_products_dataset.csv
olist_sellers_dataset.csv
```

### Step 4: Load Data into DuckDB

Once you have all CSV files in `data/raw/`, run:

```bash
python scripts/load_raw_data.py
```

This will create `ecommerce_raw.duckdb` with all tables loaded.

## Troubleshooting

### Missing CSV files
- Make sure you downloaded and extracted all files from Kaggle
- Verify all 8 CSV files are in the `data/raw/` directory

### Permission errors
- Ensure you have write permissions in the project directory

## Dataset License

The dataset is released under CC BY-NC-SA 4.0 license. It's free to use for educational and non-commercial purposes.

## Next Steps

After downloading the dataset, proceed to:
1. Run the exploratory data analysis notebook
2. Load data into DuckDB
3. Begin dbt transformations
