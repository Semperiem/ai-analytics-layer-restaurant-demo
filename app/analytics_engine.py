"""Governed metrics layer for the restaurant analytics demo.

Every metric is a plain, explicit SQL query against the `fact_sales` view
(built by scripts/build_duckdb.py) plus the dimension tables. Each function
returns a MetricResult so the SQL, the result table, and a short business
answer can all be shown to the user together.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "warehouse" / "restaurant.duckdb"


@dataclass
class MetricResult:
    metric: str
    sql: str
    df: pd.DataFrame
    answer: str


def get_connection(db_path: Path = DB_PATH) -> duckdb.DuckDBPyConnection:
    if not db_path.exists():
        raise FileNotFoundError(
            f"DuckDB warehouse not found at {db_path}. "
            "Run `python scripts/build_duckdb.py` first."
        )
    return duckdb.connect(str(db_path), read_only=True)


def _run(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame:
    return con.execute(sql).fetchdf()


def total_revenue(con: duckdb.DuckDBPyConnection) -> MetricResult:
    sql = "SELECT SUM(revenue) AS total_revenue FROM fact_sales"
    df = _run(con, sql)
    value = df["total_revenue"].iloc[0]
    answer = f"Total revenue across all stores and channels is ${value:,.2f}."
    return MetricResult("total_revenue", sql, df, answer)


def average_order_value(con: duckdb.DuckDBPyConnection) -> MetricResult:
    sql = (
        "SELECT SUM(revenue) / COUNT(DISTINCT order_id) AS average_order_value "
        "FROM fact_sales"
    )
    df = _run(con, sql)
    value = df["average_order_value"].iloc[0]
    answer = f"The average order value is ${value:,.2f}."
    return MetricResult("average_order_value", sql, df, answer)


def revenue_by_store(con: duckdb.DuckDBPyConnection) -> MetricResult:
    sql = """
        SELECT s.store_name, s.region, SUM(f.revenue) AS revenue
        FROM fact_sales f
        JOIN stores s ON f.store_id = s.store_id
        GROUP BY s.store_name, s.region
        ORDER BY revenue DESC
    """
    df = _run(con, sql)
    top = df.iloc[0]
    answer = (
        f"{top['store_name']} ({top['region']}) leads with ${top['revenue']:,.2f} "
        f"in revenue, out of {len(df)} stores."
    )
    return MetricResult("revenue_by_store", sql, df, answer)


def revenue_by_channel(con: duckdb.DuckDBPyConnection) -> MetricResult:
    sql = """
        SELECT channel, SUM(revenue) AS revenue
        FROM fact_sales
        GROUP BY channel
        ORDER BY revenue DESC
    """
    df = _run(con, sql)
    top = df.iloc[0]
    answer = f"{top['channel']} is the top channel with ${top['revenue']:,.2f} in revenue."
    return MetricResult("revenue_by_channel", sql, df, answer)


def revenue_trend(con: duckdb.DuckDBPyConnection) -> MetricResult:
    sql = """
        SELECT DATE_TRUNC('month', order_date) AS month, SUM(revenue) AS revenue
        FROM fact_sales
        GROUP BY month
        ORDER BY month
    """
    df = _run(con, sql)
    first, last = df.iloc[0], df.iloc[-1]
    answer = (
        f"Monthly revenue went from ${first['revenue']:,.2f} in {first['month'].date()} "
        f"to ${last['revenue']:,.2f} in {last['month'].date()} across {len(df)} months."
    )
    return MetricResult("revenue_trend", sql, df, answer)


def repeat_customer_count(con: duckdb.DuckDBPyConnection) -> MetricResult:
    sql = """
        WITH orders_per_customer AS (
            SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
            FROM orders
            GROUP BY customer_id
        )
        SELECT
            COUNT(*) FILTER (WHERE order_count > 1) AS repeat_customers,
            COUNT(*) AS total_customers
        FROM orders_per_customer
    """
    df = _run(con, sql)
    repeat = int(df["repeat_customers"].iloc[0])
    total = int(df["total_customers"].iloc[0])
    pct = (repeat / total * 100) if total else 0
    answer = f"{repeat} of {total} customers ({pct:.1f}%) placed more than one order."
    return MetricResult("repeat_customer_count", sql, df, answer)


def top_products(con: duckdb.DuckDBPyConnection, limit: int = 10) -> MetricResult:
    sql = f"""
        SELECT p.product_name, p.category, SUM(f.revenue) AS revenue
        FROM fact_sales f
        JOIN products p ON f.product_id = p.product_id
        GROUP BY p.product_name, p.category
        ORDER BY revenue DESC
        LIMIT {limit}
    """
    df = _run(con, sql)
    top = df.iloc[0]
    answer = (
        f"{top['product_name']} ({top['category']}) is the top seller with "
        f"${top['revenue']:,.2f} in revenue."
    )
    return MetricResult("top_products", sql, df, answer)


METRICS = {
    "total_revenue": total_revenue,
    "average_order_value": average_order_value,
    "revenue_by_store": revenue_by_store,
    "revenue_by_channel": revenue_by_channel,
    "revenue_trend": revenue_trend,
    "repeat_customer_count": repeat_customer_count,
    "top_products": top_products,
}

# Sample questions -> metric key, used for deterministic rule-based routing.
# Order matters: more specific keyword checks are listed first so a generic
# word like "revenue" doesn't shadow a more specific question.
SAMPLE_QUESTIONS = [
    ("What are the top selling products?", "top_products"),
    ("How many repeat customers do we have?", "repeat_customer_count"),
    ("What is the monthly revenue trend?", "revenue_trend"),
    ("What is revenue by channel?", "revenue_by_channel"),
    ("What is revenue by store?", "revenue_by_store"),
    ("What is the average order value?", "average_order_value"),
    ("What is total revenue?", "total_revenue"),
]

_ROUTING_RULES = [
    (("top", "product"), "top_products"),
    (("repeat", "customer"), "repeat_customer_count"),
    (("trend",), "revenue_trend"),
    (("month",), "revenue_trend"),
    (("channel",), "revenue_by_channel"),
    (("store",), "revenue_by_store"),
    (("average order value",), "average_order_value"),
    (("aov",), "average_order_value"),
    (("revenue",), "total_revenue"),
]


def route_question(question: str) -> str | None:
    """Deterministic keyword router: maps a free-text question to a metric key.

    No LLM required. Returns None if no rule matches.
    """
    q = question.lower()
    for keywords, metric in _ROUTING_RULES:
        if all(k in q for k in keywords):
            return metric
    return None


def answer_question(con: duckdb.DuckDBPyConnection, question: str) -> MetricResult | None:
    metric = route_question(question)
    if metric is None:
        return None
    return METRICS[metric](con)
