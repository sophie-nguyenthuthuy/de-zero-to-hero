"""
SQLAlchemy — Kết nối Python với PostgreSQL
"""
import logging

import pandas as pd
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection string
DB_URL = "postgresql://deuser:depassword123@localhost:5432/de_lab"


def get_engine():
    return create_engine(
        DB_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )


def query_to_dataframe(sql: str, params: dict = None) -> pd.DataFrame:
    """Execute SQL và trả về DataFrame"""
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn, params=params)
    return df


def run_transaction(operations: list[str]) -> None:
    """Chạy nhiều SQL trong một transaction — ACID!"""
    engine = get_engine()
    with engine.begin() as conn:   # Auto commit/rollback
        for sql in operations:
            conn.execute(text(sql))
    logger.info(f"Transaction hoàn tất: {len(operations)} operations")


if __name__ == "__main__":
    # Query doanh thu theo tháng
    sql = """
        SELECT
            DATE_TRUNC('month', order_date) AS month,
            COUNT(*) AS orders,
            SUM(total_amount) AS revenue
        FROM orders
        WHERE status = 'completed'
        GROUP BY 1
        ORDER BY 1
    """

    df = query_to_dataframe(sql)
    print("=== Doanh thu theo tháng ===")
    print(df.to_string())

    # Demo transaction
    print("\n=== Transaction Demo ===")
    try:
        run_transaction([
            "INSERT INTO customers(customer_id,full_name,email) "
            "VALUES('C099','Test User','test@test.com')",
            "UPDATE orders SET status='completed' WHERE order_id = 9",
        ])
        print("✅ Transaction committed")
    except Exception as e:
        print(f"❌ Transaction rolled back: {e}")
