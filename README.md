# E-Commerce Customer Intelligence Platform

End-to-end ML-powered analytics platform for customer lifetime value prediction, churn prevention, and personalized recommendations using Brazilian e-commerce data.

## Overview

This project demonstrates a production-grade data analytics and machine learning pipeline, featuring:

- **Modern Data Stack**: DuckDB + dbt for transformation
- **Machine Learning**: MLflow for experiment tracking and model registry
- **Business Intelligence**: Interactive Streamlit dashboards and Power BI reports
- **Analytics Engineering**: Dimensional modeling with star schema design
- **CI/CD**: Automated testing and deployment pipelines

## Tech Stack

- **Database**: DuckDB 0.9.2+
- **Transformation**: dbt-duckdb 1.7.0+
- **ML Platform**: MLflow 2.9.2+
- **ML Libraries**: scikit-learn, XGBoost, Optuna
- **Visualization**: Streamlit, Plotly, Power BI
- **Code Quality**: SQLFluff

## Project Status

✅ **Phase 1: Foundation & Data Exploration** - Complete
- Data loaded into DuckDB
- Comprehensive EDA completed
- Data quality documented
- Data dictionary created

✅ **Phase 2: dbt Transformation Layer** - Complete
- Staging models (8 clean, standardized views)
- Intermediate models (RFM, customer/product/seller aggregations)
- Mart models (star schema with 3 dimensions + 2 fact tables)
- Data quality tests (unique, not null, referential integrity)
- Full documentation with lineage

🚧 **Phase 3: Business Intelligence Dashboards** - Next

## Quick Start

### Prerequisites

- Python 3.11+
- 8 GB RAM (16 GB recommended)
- Kaggle account (for dataset download)

### Initial Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/dbt-ml-analytics-pipeline.git
cd dbt-ml-analytics-pipeline
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download the dataset from Kaggle**
   - Visit [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
   - Download all CSV files
   - Extract to `data/raw/` directory

   Expected files:
   ```
   data/raw/
   ├── olist_customers_dataset.csv
   ├── olist_geolocation_dataset.csv
   ├── olist_order_items_dataset.csv
   ├── olist_order_payments_dataset.csv
   ├── olist_order_reviews_dataset.csv
   ├── olist_orders_dataset.csv
   ├── olist_products_dataset.csv
   ├── olist_sellers_dataset.csv
   └── product_category_name_translation.csv
   ```

5. **Load data into DuckDB (REQUIRED FIRST STEP)**

   ⚠️ **Important**: You must run this script before exploring the data or running notebooks!

   ```bash
   python scripts/load_raw_data.py
   ```

   This script will:
   - Read all CSV files from `data/raw/`
   - Create `ecommerce_raw.duckdb` database
   - Load data into `raw` schema (9 tables)
   - Validate data loaded successfully

   Expected output:
   ```
   Loading Olist E-Commerce data into DuckDB...
   ✓ Loaded olist_customers_dataset: 99,441 rows
   ✓ Loaded olist_orders_dataset: 99,441 rows
   ...
   ✓ All data loaded successfully!
   Database: ecommerce_raw.duckdb
   ```

6. **Run dbt transformations**

   Transform raw data into analytics-ready tables:

   ```bash
   cd dbt/ecommerce_analytics
   dbt run --profiles-dir ..
   dbt test --profiles-dir ..
   ```

   This creates 17 models:
   - **Staging** (8 views): Cleaned raw data
   - **Intermediate** (4 views): Business logic (RFM, aggregations)
   - **Marts** (5 tables): Star schema for analytics

   See [dbt/ecommerce_analytics/GETTING_STARTED.md](dbt/ecommerce_analytics/GETTING_STARTED.md) for details.

7. **Explore the data**
```bash
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
```

### Useful Commands

```bash
# View database contents with DuckDB CLI
duckdb ecommerce_raw.duckdb

# In DuckDB CLI (raw data):
SHOW TABLES;
SELECT COUNT(*) FROM raw.olist_orders_dataset;

# In DuckDB CLI (transformed data):
SELECT * FROM marts.dim_customers LIMIT 5;
SELECT customer_segment, COUNT(*) FROM marts.dim_customers GROUP BY 1;
.quit

# Run dbt transformations
cd dbt/ecommerce_analytics
dbt run --profiles-dir ..          # Build all models
dbt test --profiles-dir ..         # Run data quality tests
dbt docs generate --profiles-dir ..  # Generate documentation
dbt docs serve --profiles-dir ..  # View lineage graph

# Run specific notebook cells
jupyter nbconvert --execute --to notebook notebooks/01_exploratory_data_analysis.ipynb
```

## Documentation

### EDA Notebook

The [01_exploratory_data_analysis.ipynb](notebooks/01_exploratory_data_analysis.ipynb) notebook contains:
- Data overview and profiling
- Comprehensive data quality checks (duplicates, nulls, referential integrity, date validation)
- Business metrics analysis (order trends, revenue, reviews)
- Portuguese-to-English translation examples
- Summary findings and recommendations for Phase 2

### dbt Models

See [dbt/ecommerce_analytics/GETTING_STARTED.md](dbt/ecommerce_analytics/GETTING_STARTED.md) for:
- How to run dbt transformations
- Model documentation and lineage
- Example SQL queries for analytics
- Troubleshooting guide

The dbt project creates:
- **8 staging models**: Clean, standardized raw data
- **4 intermediate models**: RFM segmentation, customer/product/seller aggregations
- **5 mart models**: Star schema (dim_customers, dim_products, dim_sellers, fct_orders, fct_order_items)

## Project Structure

```
dbt-ml-analytics-pipeline/
├── data/
│   ├── raw/                        # Raw CSV files from Kaggle (gitignored)
│   └── processed/                  # Processed data files
├── notebooks/
│   └── 01_exploratory_data_analysis.ipynb  # EDA with data quality checks
├── scripts/
│   └── load_raw_data.py            # ⚠️ MUST RUN FIRST - Loads CSVs into DuckDB
├── models/                         # ML models and training scripts (Phase 4)
├── dbt/                            # ✅ dbt project (Phase 2 - COMPLETE)
│   ├── profiles.yml                # DuckDB connection config
│   └── ecommerce_analytics/        # Main dbt project
│       ├── dbt_project.yml         # Project settings
│       ├── GETTING_STARTED.md      # dbt usage guide
│       └── models/                 # 17 SQL models (staging, intermediate, marts)
├── dashboards/                     # Streamlit and Power BI dashboards (Phase 3)
├── tests/                          # Unit and integration tests
├── ecommerce_raw.duckdb            # DuckDB database (gitignored)
├── DATA_DICTIONARY.md              # Comprehensive data documentation
├── README.md                       # This file
└── requirements.txt                # Python dependencies
```

## Dataset Information

**Source**: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

**Coverage**:
- 100K orders from September 2016 to August 2018
- 9 related tables (customers, orders, items, payments, reviews, products, sellers, geolocation, translations)
- Brazilian marketplace data
- Real commercial data (anonymized)

**Key Statistics**:
- 99,441 orders (97% delivered)
- 96K unique customers
- 32,951 products
- 3,095 sellers
- 99,224 reviews (avg ~4+ stars)

## Roadmap

- [x] **Phase 1**: Foundation & Data Exploration
  - [x] Download and load dataset
  - [x] Comprehensive EDA
  - [x] Data quality assessment
  - [x] Create data dictionary
- [x] **Phase 2**: dbt Transformation Layer
  - [x] Staging models (8 clean, standardized views)
  - [x] Intermediate models (RFM, customer/product/seller aggregations)
  - [x] Mart models (star schema: 3 dims + 2 facts)
  - [x] Data quality tests (unique, not null, referential integrity)
  - [x] Model documentation and lineage
  - [ ] CI/CD with GitHub Actions (optional)
- [ ] **Phase 3**: Business Intelligence Dashboards
- [ ] **Phase 4**: ML Pipeline with MLflow
- [ ] **Phase 5**: Documentation & Polish
- [ ] **Phase 6**: AWS Deployment (Optional)

## License

MIT