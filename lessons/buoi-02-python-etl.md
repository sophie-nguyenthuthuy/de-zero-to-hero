# 🐍 Buổi 2 — Python cho Data Engineering

**Data Engineer: Zero to Hero | Phase 1 – Engineering Foundations**
Thời gian: 2.5 tiếng | Lab: 60 phút (80–140 phút)

## 🎯 Mục tiêu Lab

- Setup môi trường Python chuyên nghiệp với `uv`
- Viết ETL script hoàn chỉnh: Extract → Transform → Load
- Xử lý CSV, JSON, Parquet với pandas
- Tạo CLI tool với argparse
- Hiểu async vs sync qua ví dụ thực tế

## 🛠 Yêu cầu

- Đã hoàn thành [Buổi 1](buoi-01-linux-shell.md) (WSL2/Ubuntu)
- Python 3.10+

---

## PHẦN 1 — Setup môi trường với uv (10 phút)

### 1.1 Cài uv — package manager hiện đại (nhanh hơn pip 10–100x)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
uv --version

mkdir -p ~/de-lab/b02-python && cd ~/de-lab/b02-python
uv init .
cat pyproject.toml
```

### 1.2 Virtual environment + packages

```bash
cd ~/de-lab/b02-python
uv venv --python 3.11
source .venv/bin/activate
which python && python --version

uv add pandas pyarrow pydantic loguru rich tqdm
uv add --dev pytest pytest-cov black ruff
uv pip list
```

### 1.3 So sánh uv vs pip

```bash
time pip install pandas pyarrow pydantic     # ~30-60 giây
time uv pip install pandas pyarrow pydantic  # ~2-5 giây
```

---

## PHẦN 2 — Python Foundations cho DE (15 phút)

### 2.1 Cấu trúc project

```bash
mkdir -p src/{extractors,transformers,loaders,utils} tests
touch src/__init__.py src/extractors/__init__.py src/transformers/__init__.py \
      src/loaders/__init__.py src/utils/__init__.py
tree . --ignore=".venv"
```

### 2.2 Data structures & comprehension

Xem [`../buoi-02-python/src/utils/data_structures.py`](../buoi-02-python/src/utils/data_structures.py) — list comprehension (lọc completed amounts), dict comprehension + `defaultdict` (group by status), set operations cho data reconciliation (missing/extra/common ids).

```bash
python src/utils/data_structures.py
```

### 2.3 Error handling đúng cách

Xem [`../buoi-02-python/src/utils/error_handling.py`](../buoi-02-python/src/utils/error_handling.py) — logging thay print, custom exceptions (`DataValidationError`, `DataExtractionError`, `SchemaError`), và **`Result[T]`** dataclass pattern (`Result.ok` / `Result.fail`) để tránh raise exception ở mọi nơi (`safe_parse_amount`, `read_file_safe`).

```bash
python src/utils/error_handling.py
```

---

## PHẦN 3 — LAB CHÍNH: ETL Pipeline (35 phút)

Pipeline phân lớp gồm Extractor → Transformer → Loader, điều phối bởi CLI `etl_pipeline.py`.

### 3.1 Extractor — đọc nhiều format

[`../buoi-02-python/src/extractors/file_extractor.py`](../buoi-02-python/src/extractors/file_extractor.py) — `FileExtractor` hỗ trợ `.csv/.json/.jsonl/.parquet`, tự nhận dạng theo extension, đọc CSV với `dtype_backend="pyarrow"`, và `extract_chunked()` cho file lớn.

### 3.2 Transformer — clean, validate, enrich

[`../buoi-02-python/src/transformers/order_transformer.py`](../buoi-02-python/src/transformers/order_transformer.py) — `OrderTransformer` chạy pipeline 9 bước: validate schema → standardize columns → handle nulls → validate amounts → validate statuses → parse dates → deduplicate → enrich (amount_tier, day_of_week, week_num, is_weekend) → add metadata. Mỗi bước log số dòng trước/sau.

### 3.3 Loader — xuất dữ liệu

[`../buoi-02-python/src/loaders/file_loader.py`](../buoi-02-python/src/loaders/file_loader.py) — `FileLoader` ghi CSV/JSON/JSONL/Parquet, hỗ trợ partition theo column, và `generate_report()` xuất báo cáo JSON (row/column count, null counts, numeric summary, status distribution, amount stats).

### 3.4 CLI ETL Script với argparse

[`../buoi-02-python/src/etl_pipeline.py`](../buoi-02-python/src/etl_pipeline.py) — điều phối Extract/Transform/Load với các tham số `--input/-i`, `--output-dir/-o`, `--output-name`, `--format/-f`, `--partition-by`, `--report`, `--dry-run`, `--verbose/-v`.

```bash
cd ~/de-lab/b02-python
python src/etl_pipeline.py --input ../data/raw/orders.csv --output-dir ../data/processed --format parquet --report --verbose
python src/etl_pipeline.py --input ../data/raw/orders.csv --dry-run
python src/etl_pipeline.py --input ../data/raw/orders.csv --output-dir ../data/processed/partitioned --format csv --partition-by status
```

> **Lưu ý path:** chạy từ `~/de-lab/b02-python/`, file `orders.csv` nằm ở `~/de-lab/data/raw/` nên dùng `../data/raw/orders.csv`. Trong repo này, `orders.csv` được đặt sẵn ở [`../buoi-02-python/data/raw/orders.csv`](../buoi-02-python/data/raw/orders.csv) để lab tự chứa — chỉnh path `--input` cho phù hợp.

### 3.5 Async I/O — sync vs async

[`../buoi-02-python/src/extractors/async_http_extractor.py`](../buoi-02-python/src/extractors/async_http_extractor.py) — demo `asyncio.gather` chạy nhiều task I/O đồng thời, so sánh thời gian sync (tuần tự) vs async, và ghi chú khi nào nên/không nên dùng async.

```bash
python src/extractors/async_http_extractor.py
```

---

## PHẦN 4 — Kiểm tra tổng kết

```bash
cd ~/de-lab/b02-python
python src/etl_pipeline.py --input ../data/raw/orders.csv --output-dir ../data/processed/b02 --format parquet --report
python -c "
import pandas as pd
df = pd.read_parquet('../data/processed/b02/orders_clean.parquet')
assert len(df) > 0 and '_processed_at' in df.columns
print(f'OK: {len(df)} rows, {len(df.columns)} columns')
"
```

---

## 📚 Homework

1. **Mở rộng Transformer**: thêm bước validate `customer_id` phải khớp `C` + 3 chữ số.
2. **Multi-format output**: cho CLI nhận nhiều `--format` cùng lúc, ghi cả CSV lẫn Parquet.
3. **Chunked processing**: xử lý file 100.000 dòng với `extract_chunked()`, đo thời gian.

---

**Buổi tiếp theo:** [Buổi 3 — Database & SQL](buoi-03-database-sql.md)
