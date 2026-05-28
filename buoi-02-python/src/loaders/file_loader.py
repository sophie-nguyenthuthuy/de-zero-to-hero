"""
File Loader — Ghi dữ liệu ra CSV, JSON, Parquet
"""
import json
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


class FileLoader:
    """Load (ghi) DataFrame ra file với nhiều format"""

    def __init__(self, base_dir: str = "data/processed"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def load(
        self,
        df: pd.DataFrame,
        filename: str,
        format: str = "parquet",
        partition_by: str | None = None,
    ) -> list[str]:
        """
        Ghi DataFrame ra file.

        Returns:
            list[str]: Danh sách đường dẫn file đã ghi
        """
        format = format.lower()

        writers = {
            "csv": self._write_csv,
            "json": self._write_json,
            "parquet": self._write_parquet,
            "jsonl": self._write_jsonl,
        }

        if format not in writers:
            raise ValueError(f"Format không hỗ trợ: {format}")

        if partition_by and partition_by in df.columns:
            return self._write_partitioned(
                df, filename, format, partition_by, writers[format]
            )

        filepath = self.base_dir / f"{filename}.{format}"
        writers[format](df, filepath)
        logger.info(f"Saved {len(df):,} rows → {filepath}")
        return [str(filepath)]

    def _write_csv(self, df: pd.DataFrame, path: Path) -> None:
        df.to_csv(path, index=False, encoding="utf-8-sig")   # BOM cho Excel compat

    def _write_json(self, df: pd.DataFrame, path: Path) -> None:
        df.to_json(
            path,
            orient="records",
            indent=2,
            force_ascii=False,
            default_handler=str,
        )

    def _write_jsonl(self, df: pd.DataFrame, path: Path) -> None:
        """JSON Lines — tốt cho streaming/append"""
        with open(path, "w", encoding="utf-8") as f:
            for record in df.to_dict(orient="records"):
                f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    def _write_parquet(self, df: pd.DataFrame, path: Path) -> None:
        df.to_parquet(path, engine="pyarrow", index=False, compression="snappy")

    def _write_partitioned(
        self, df, filename, format, partition_col, writer_fn
    ) -> list[str]:
        """Ghi nhiều file theo partition"""
        output_files = []

        for partition_val, partition_df in df.groupby(partition_col):
            safe_val = str(partition_val).replace("/", "_")
            filepath = self.base_dir / f"{filename}_{partition_col}={safe_val}.{format}"
            writer_fn(partition_df.drop(columns=[partition_col]), filepath)
            output_files.append(str(filepath))
            logger.info(
                f"  Partition {partition_col}={partition_val}: "
                f"{len(partition_df):,} rows → {filepath.name}"
            )

        return output_files

    def generate_report(self, df: pd.DataFrame, report_path: str) -> None:
        """Tạo báo cáo JSON từ DataFrame"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.dtypes.apply(str).to_dict(),
            "null_counts": df.isnull().sum().to_dict(),
            "numeric_summary": df.select_dtypes(include="number").describe().to_dict(),
        }

        if "status" in df.columns:
            report["status_distribution"] = df["status"].value_counts().to_dict()
        if "amount" in df.columns:
            report["amount_stats"] = {
                "total": float(df["amount"].sum()),
                "mean": float(df["amount"].mean()),
                "median": float(df["amount"].median()),
            }

        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"Report saved: {report_path}")
