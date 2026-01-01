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

🚧 **Phase 1: Foundation & Data Exploration** - In Progress

## Quick Start

### Prerequisites

- Python 3.11+
- 8 GB RAM (16 GB recommended)

### Setup

1. Clone the repository
```bash
git clone https://github.com/yourusername/dbt-ml-analytics-pipeline.git
cd dbt-ml-analytics-pipeline
```

2. Create and activate virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Download the Olist dataset from [Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) and extract all CSV files to `data/raw/`

5. Load data into DuckDB
```bash
python scripts/load_raw_data.py
```

6. Explore the data
```bash
jupyter notebook notebooks/01_exploratory_data_analysis.ipynb
```

## Project Structure

```
dbt-ml-analytics-pipeline/
├── data/
│   ├── raw/              # Raw CSV files from Kaggle
│   └── processed/        # Processed data files
├── notebooks/            # Jupyter notebooks for EDA and experiments
├── scripts/              # Data loading and utility scripts
├── models/               # ML models and training scripts
├── dbt/                  # dbt project (coming in Phase 2)
├── dashboards/           # Streamlit and Power BI dashboards
├── tests/                # Unit and integration tests
└── docs/                 # Documentation
```

## Roadmap

- [ ] **Phase 1**: Foundation & Data Exploration
- [ ] **Phase 2**: dbt Transformation Layer
- [ ] **Phase 3**: Business Intelligence Dashboards
- [ ] **Phase 4**: ML Pipeline with MLflow
- [ ] **Phase 5**: Documentation & Polish
- [ ] **Phase 6**: AWS Deployment (Optional)

## License

MIT