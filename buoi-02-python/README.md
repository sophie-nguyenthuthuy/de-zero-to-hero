# Buổi 2 — Python cho Data Engineering (Lab)

Code lab cho [Buổi 2](../lessons/buoi-02-python-etl.md). ETL pipeline phân lớp + CLI, quản lý bằng [`uv`](https://github.com/astral-sh/uv).

## Cấu trúc

```
buoi-02-python/
├── pyproject.toml
├── data/raw/orders.csv
└── src/
    ├── etl_pipeline.py            # CLI điều phối Extract → Transform → Load
    ├── extractors/
    │   ├── file_extractor.py      # CSV/JSON/JSONL/Parquet + chunked
    │   └── async_http_extractor.py # demo sync vs async
    ├── transformers/order_transformer.py  # pipeline 9 bước validate/clean/enrich
    ├── loaders/file_loader.py     # ghi multi-format + partition + report JSON
    └── utils/                     # data_structures.py, error_handling.py
```

## Setup

```bash
cd buoi-02-python
uv venv --python 3.11
source .venv/bin/activate
uv sync                  # cài deps từ pyproject.toml
# hoặc: uv add pandas pyarrow pydantic loguru rich tqdm
```

## Chạy

```bash
# ETL cơ bản (chạy từ thư mục buoi-02-python)
python src/etl_pipeline.py --input data/raw/orders.csv --output-dir data/processed --format parquet --report

# Dry-run (không ghi file)
python src/etl_pipeline.py --input data/raw/orders.csv --dry-run

# Partition theo status
python src/etl_pipeline.py --input data/raw/orders.csv --partition-by status --format csv

# Demo không cần pandas
python src/utils/data_structures.py
python src/extractors/async_http_extractor.py
```

## Yêu cầu

- Python 3.10+
- `pandas`, `pyarrow` (+ `pydantic`, `loguru`, `rich`, `tqdm`)
- `data_structures.py` và `async_http_extractor.py` chỉ dùng stdlib — chạy được ngay không cần cài deps.
