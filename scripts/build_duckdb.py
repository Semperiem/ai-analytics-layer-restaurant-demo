"""Build a local DuckDB warehouse from the synthetic restaurant CSV files.

Reproducible: delete warehouse/restaurant.duckdb and re-run this script to
regenerate the database from the CSV files checked into data/synthetic/.
"""
from pathlib import Path
import duckdb

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "synthetic"
WAREHOUSE_DIR = ROOT / "warehouse"
DB_PATH = WAREHOUSE_DIR / "restaurant.duckdb"

RAW_TABLES = {
    "stores": "stores.csv",
    "products": "products.csv",
    "customers": "customers.csv",
    "orders": "orders.csv",
    "order_items": "order_items.csv",
}


def build(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    con = duckdb.connect(str(db_path))

    for table, csv_name in RAW_TABLES.items():
        csv_path = DATA_DIR / csv_name
        con.execute(
            f"CREATE TABLE {table} AS SELECT * FROM read_csv_auto(?)",
            [str(csv_path)],
        )

    # Mirrors dbt_restaurant/models/staging + marts so the DuckDB demo and the
    # dbt project agree on the same transformation logic.
    con.execute("CREATE VIEW stg_orders AS SELECT * FROM orders")
    con.execute("CREATE VIEW stg_order_items AS SELECT * FROM order_items")
    con.execute(
        """
        CREATE VIEW fact_sales AS
        SELECT
            oi.order_id,
            o.order_date,
            o.customer_id,
            o.store_id,
            o.channel,
            oi.product_id,
            oi.quantity,
            oi.unit_cost,
            oi.unit_price,
            oi.quantity * oi.unit_price AS revenue,
            oi.quantity * (oi.unit_price - oi.unit_cost) AS gross_margin
        FROM stg_order_items oi
        JOIN stg_orders o ON oi.order_id = o.order_id
        """
    )

    con.close()
    print(f"Built DuckDB warehouse at {db_path}")


if __name__ == "__main__":
    build()
