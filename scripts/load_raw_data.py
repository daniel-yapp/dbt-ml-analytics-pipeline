"""Load raw CSV files from Olist dataset into DuckDB."""

import duckdb
from pathlib import Path


def load_raw_data():
    """Load all CSV files into DuckDB raw schema."""

    project_root = Path(__file__).parent.parent
    raw_data_dir = project_root / "data" / "raw"
    db_path = project_root / "ecommerce.duckdb"

    # Check for CSV files
    csv_files = list(raw_data_dir.glob("*.csv"))
    if not csv_files:
        print("No CSV files found. Run: python scripts/download_data.py")
        return

    print(f"Loading {len(csv_files)} tables into {db_path.name}...\n")

    # Connect and create schema
    con = duckdb.connect(str(db_path))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # Load each CSV
    for csv_file in sorted(csv_files):
        table_name = csv_file.stem
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.{table_name} AS
            SELECT * FROM read_csv_auto('{csv_file}')
        """)

        row_count = con.execute(f"SELECT COUNT(*) FROM raw.{table_name}").fetchone()[0]
        print(f"[OK] {table_name}: {row_count:,} rows")

    con.close()
    print(f"\nComplete! Database: {db_path}")


if __name__ == "__main__":
    load_raw_data()
