"""Download Olist dataset from Kaggle and load into DuckDB.

This script combines data download and loading into a single operation.
Can be configured to use Kaggle API credentials from multiple sources.
"""

import os
import zipfile
from pathlib import Path
import duckdb


def setup_kaggle_credentials(api_token=None, username=None, key=None):
    """
    Set up Kaggle API credentials (supports both new token and legacy formats).

    Priority order:
    1. New format: KAGGLE_API_TOKEN environment variable or api_token parameter
    2. Legacy format: KAGGLE_USERNAME + KAGGLE_KEY or username/key parameters
    3. ~/.kaggle/kaggle.json

    Args:
        api_token: Kaggle API token (new format, optional)
        username: Kaggle username (legacy format, optional)
        key: Kaggle API key (legacy format, optional)
    """
    # NEW FORMAT: Single token
    if api_token:
        os.environ['KAGGLE_API_TOKEN'] = api_token
        print("Using provided Kaggle API token (new format)")
    elif os.getenv('KAGGLE_API_TOKEN'):
        print("Using Kaggle API token from environment variable (new format)")
    # LEGACY FORMAT: Username + Key
    elif username and key:
        os.environ['KAGGLE_USERNAME'] = username
        os.environ['KAGGLE_KEY'] = key
        print("Using provided Kaggle credentials (legacy format)")
    elif os.getenv('KAGGLE_USERNAME') and os.getenv('KAGGLE_KEY'):
        print("Using Kaggle credentials from environment variables (legacy format)")
    else:
        kaggle_json = Path.home() / '.kaggle' / 'kaggle.json'
        if kaggle_json.exists():
            print(f"Using Kaggle credentials from {kaggle_json}")
        else:
            raise ValueError(
                "Kaggle credentials not found! Please provide them via:\n"
                "\nNEW FORMAT (recommended):\n"
                "  - Environment: export KAGGLE_API_TOKEN='your_token_here'\n"
                "  - Parameter: download_and_load_data(api_token='your_token_here')\n"
                "\nLEGACY FORMAT:\n"
                "  - Environment: export KAGGLE_USERNAME='...' KAGGLE_KEY='...'\n"
                "  - Parameters: download_and_load_data(username='...', key='...')\n"
                "  - File: ~/.kaggle/kaggle.json"
            )


def download_kaggle_dataset(dataset_name, download_path, api_token=None, username=None, key=None):
    """
    Download dataset from Kaggle.

    Args:
        dataset_name: Kaggle dataset identifier (e.g., 'olistbr/brazilian-ecommerce')
        download_path: Path to download dataset to
        api_token: Kaggle API token (new format, optional)
        username: Kaggle username (legacy format, optional)
        key: Kaggle API key (legacy format, optional)
    """
    from kaggle.api.kaggle_api_extended import KaggleApi

    # Set up credentials
    setup_kaggle_credentials(api_token, username, key)

    # Initialize Kaggle API
    api = KaggleApi()
    api.authenticate()

    print(f"\nDownloading dataset: {dataset_name}")
    print(f"Destination: {download_path}")

    # Download dataset (unzip=True will extract the files)
    api.dataset_download_files(
        dataset_name,
        path=download_path,
        unzip=True
    )

    print("Download complete!")


def load_csv_to_duckdb(csv_dir, db_path, schema='raw'):
    """
    Load all CSV files from a directory into DuckDB.

    Args:
        csv_dir: Directory containing CSV files
        db_path: Path to DuckDB database file
        schema: Schema name to create tables in (default: 'raw')
    """
    csv_files = list(Path(csv_dir).glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}")

    print(f"\nLoading {len(csv_files)} CSV files into {db_path.name}")
    print(f"Schema: {schema}\n")

    # Connect and create schema
    con = duckdb.connect(str(db_path))
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    # Load each CSV
    for csv_file in sorted(csv_files):
        table_name = csv_file.stem

        # Create or replace table
        con.execute(f"""
            CREATE OR REPLACE TABLE {schema}.{table_name} AS
            SELECT * FROM read_csv_auto('{csv_file}')
        """)

        row_count = con.execute(f"SELECT COUNT(*) FROM {schema}.{table_name}").fetchone()[0]
        print(f"[OK] {table_name}: {row_count:,} rows")

    con.close()
    print(f"\nComplete! Database: {db_path}")


def download_and_load_data(
    kaggle_api_token=None,
    kaggle_username=None,
    kaggle_key=None,
    dataset_name='olistbr/brazilian-ecommerce',
    project_root=None,
    db_name='ecommerce.duckdb'
):
    """
    Download Olist dataset from Kaggle and load into DuckDB.

    Args:
        kaggle_api_token: Kaggle API token (new format, optional)
        kaggle_username: Kaggle username (legacy format, optional)
        kaggle_key: Kaggle API key (legacy format, optional)
        dataset_name: Kaggle dataset identifier
        project_root: Project root directory (defaults to parent of scripts/)
        db_name: Database filename

    Returns:
        Path to created database
    """
    # Determine paths
    if project_root is None:
        project_root = Path(__file__).parent.parent
    else:
        project_root = Path(project_root)

    raw_data_dir = project_root / "data" / "raw"
    db_path = project_root / db_name

    # Create data directory
    raw_data_dir.mkdir(parents=True, exist_ok=True)

    # Download dataset from Kaggle
    print("="*60)
    print("STEP 1: DOWNLOADING DATA FROM KAGGLE")
    print("="*60)

    download_kaggle_dataset(
        dataset_name=dataset_name,
        download_path=raw_data_dir,
        api_token=kaggle_api_token,
        username=kaggle_username,
        key=kaggle_key
    )

    # Load into DuckDB
    print("\n" + "="*60)
    print("STEP 2: LOADING DATA INTO DUCKDB")
    print("="*60)

    load_csv_to_duckdb(
        csv_dir=raw_data_dir,
        db_path=db_path,
        schema='raw'
    )

    print("\n" + "="*60)
    print("SUCCESS! Data pipeline complete")
    print("="*60)
    print(f"Database: {db_path}")
    print(f"Run 'dbt run' to build analytics models")

    return db_path


if __name__ == "__main__":
    download_and_load_data()
