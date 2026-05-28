"""
File Extractor — Hỗ trợ CSV, JSON, Parquet
"""
import json
import logging
from pathlib import Path
from typing import Iterator

import pandas as pd

logger = logging.getLogger(__name__)


class FileExtractor:
    """Extract data từ nhiều loại file"""

    SUPPORTED_FORMATS = [".csv", ".json", ".parquet", ".jsonl"]

    def __init__(self, chunk_size: int = 10_000):
        self.chunk_size = chunk_size

    def extract(self, filepath: str) -> pd.DataFrame:
        """
        Đọc file và trả về DataFrame.
        Tự động nhận dạng format dựa vào extension.
        """
        path = Path(filepath)

        if not path.exists():
            raise FileNotFoundError(f"File không tồn tại: {filepath}")

        ext = path.suffix.lower()
        logger.info(f"Extracting: {filepath} (format={ext})")

        readers = {
            ".csv": self._read_csv,
            ".json": self._read_json,
            ".jsonl": self._read_jsonl,
            ".parquet": self._read_parquet,
        }

        if ext not in readers:
            raise ValueError(
                f"Format không hỗ trợ: {ext}. Hỗ trợ: {self.SUPPORTED_FORMATS}"
            )

        df = readers[ext](path)
        logger.info(
            f"Extracted {len(df):,} rows, {len(df.columns)} columns from {path.name}"
        )
        return df

    def _read_csv(self, path: Path) -> pd.DataFrame:
        return pd.read_csv(
            path,
            encoding="utf-8-sig",   # Xử lý BOM từ Excel
            dtype_backend="pyarrow",
            on_bad_lines="warn",
        )

    def _read_json(self, path: Path) -> pd.DataFrame:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Xử lý cả array và object
        if isinstance(data, list):
            return pd.DataFrame(data)
        elif isinstance(data, dict):
            # Tìm key chứa array records
            for key, value in data.items():
                if isinstance(value, list):
                    return pd.DataFrame(value)
            return pd.DataFrame([data])

        raise ValueError(
            "JSON format không hỗ trợ — cần array hoặc object với array field"
        )

    def _read_jsonl(self, path: Path) -> pd.DataFrame:
        """JSON Lines — mỗi dòng là một JSON object"""
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    logger.warning(f"Skip dòng {i} — JSON lỗi: {e}")
        return pd.DataFrame(records)

    def _read_parquet(self, path: Path) -> pd.DataFrame:
        return pd.read_parquet(path, engine="pyarrow")

    def extract_chunked(self, filepath: str) -> Iterator[pd.DataFrame]:
        """Đọc file CSV theo chunks — cho file lớn"""
        path = Path(filepath)
        if path.suffix.lower() != ".csv":
            raise ValueError("Chunked reading chỉ hỗ trợ CSV")

        logger.info(f"Chunked reading: {filepath} (chunk_size={self.chunk_size:,})")

        for i, chunk in enumerate(pd.read_csv(filepath, chunksize=self.chunk_size)):
            logger.info(f"  Chunk {i + 1}: {len(chunk):,} rows")
            yield chunk


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    extractor = FileExtractor()

    # Test CSV
    df = extractor.extract("data/raw/orders.csv")
    print(f"\nCSV extracted: {df.shape}")
    print(df.dtypes)
    print(df.head(3))
