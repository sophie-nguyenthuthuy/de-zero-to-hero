"""
Order Transformer — Clean, validate, enrich order data
"""
import logging
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class OrderTransformer:
    """Transform và validate order DataFrame"""

    REQUIRED_COLUMNS = ["order_id", "customer_id", "product", "amount", "status", "date"]
    VALID_STATUSES = {"completed", "pending", "cancelled", "failed", "in_progress"}

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Chạy toàn bộ transformation pipeline"""
        logger.info(f"Starting transformation: {len(df):,} rows")

        steps = [
            ("Validate schema", self._validate_schema),
            ("Standardize columns", self._standardize_columns),
            ("Handle nulls", self._handle_nulls),
            ("Validate amounts", self._validate_amounts),
            ("Validate statuses", self._validate_statuses),
            ("Parse dates", self._parse_dates),
            ("Deduplicate", self._deduplicate),
            ("Enrich data", self._enrich),
            ("Add metadata", self._add_metadata),
        ]

        result = df.copy()
        stats = {"input_rows": len(df)}

        for step_name, step_fn in steps:
            try:
                before = len(result)
                result = step_fn(result)
                after = len(result)
                dropped = before - after
                logger.info(
                    f"  [{step_name}] {before:,} → {after:,} rows"
                    + (f" (dropped {dropped:,})" if dropped else "")
                )
            except Exception as e:
                logger.error(f"  [{step_name}] FAILED: {e}")
                raise

        stats["output_rows"] = len(result)
        stats["drop_rate"] = f"{(1 - stats['output_rows'] / stats['input_rows']) * 100:.1f}%"
        logger.info(f"Transformation complete: {stats}")

        return result

    def _validate_schema(self, df: pd.DataFrame) -> pd.DataFrame:
        missing = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(f"Thiếu columns: {missing}")
        return df[self.REQUIRED_COLUMNS]   # Chỉ giữ cột cần thiết

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Lowercase, strip whitespace"""
        df = df.copy()
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        return df

    def _handle_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        # Drop rows thiếu các field bắt buộc
        required_not_null = ["order_id", "customer_id", "amount"]
        df = df.dropna(subset=required_not_null)
        # Fill optional fields
        df["status"] = df["status"].fillna("unknown")
        return df

    def _validate_amounts(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        invalid_mask = df["amount"].isna() | (df["amount"] < 0)

        invalid_count = invalid_mask.sum()
        if invalid_count > 0:
            logger.warning(f"  Loại bỏ {invalid_count} dòng amount không hợp lệ")

        return df[~invalid_mask].copy()

    def _validate_statuses(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        invalid_statuses = ~df["status"].isin(self.VALID_STATUSES)
        if invalid_statuses.any():
            bad = df[invalid_statuses]["status"].unique()
            logger.warning(f"  Thay thế status không hợp lệ: {bad} → 'unknown'")
            df.loc[invalid_statuses, "status"] = "unknown"
        return df

    def _parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        invalid = df["date"].isna().sum()
        if invalid > 0:
            logger.warning(f"  {invalid} dòng có date không parse được — loại bỏ")
            df = df.dropna(subset=["date"])
        return df

    def _deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        before = len(df)
        df = df.drop_duplicates(subset=["order_id"], keep="last")
        if len(df) < before:
            logger.warning(f"  Removed {before - len(df)} duplicate order_ids")
        return df

    def _enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """Thêm các derived columns"""
        df = df.copy()
        # Amount tiers
        df["amount_tier"] = pd.cut(
            df["amount"],
            bins=[0, 1_000_000, 5_000_000, 10_000_000, float("inf")],
            labels=["low", "medium", "high", "premium"],
            right=False,
        )
        # Day of week
        df["day_of_week"] = df["date"].dt.day_name()
        # Week number
        df["week_num"] = df["date"].dt.isocalendar().week.astype(int)
        # Is weekend
        df["is_weekend"] = df["date"].dt.dayofweek >= 5
        return df

    def _add_metadata(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["_processed_at"] = datetime.now().isoformat()
        df["_source"] = "orders_etl_v1"
        return df


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    # Test data
    raw_data = pd.DataFrame(
        {
            "order_id": [1001, 1002, 1003, 1001, 1004],   # 1001 duplicate
            "customer_id": ["C001", "C002", None, "C004", "C005"],
            "product": ["Laptop", "Phone", "Tablet", "Laptop", "Monitor"],
            "amount": [15000000, -100, 12000000, 15000000, 5000000],
            "status": ["completed", "completed", "PENDING", "done", "completed"],
            "date": ["2024-01-15", "2024-01-16", "invalid", "2024-01-15", "2024-01-18"],
        }
    )

    transformer = OrderTransformer()
    result = transformer.transform(raw_data)

    print("\n=== Kết quả Transformation ===")
    print(result.to_string())
