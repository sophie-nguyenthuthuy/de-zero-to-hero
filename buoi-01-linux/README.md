# Buổi 1 — Linux, Shell & Dev Environment (Lab)

Code lab cho [Buổi 1](../lessons/buoi-01-linux-shell.md). Lab Bash: web crawler + data quality + automation.

## Cấu trúc

```
buoi-01-linux/
├── Makefile               # Workflow automation
├── data/raw/orders.csv    # Dữ liệu mẫu
└── scripts/
    ├── web_crawler.sh     # CLI crawler (retry, extract text, lọc keyword)
    ├── check_data.sh      # Data quality check + thống kê
    ├── batch_process.sh   # Xử lý nhiều CSV trong thư mục
    └── lab_check.sh        # Checklist PASS/FAIL (thiết kế cho môi trường ~/de-lab)
```

## Chạy

```bash
cd buoi-01-linux

# Data quality check
./scripts/check_data.sh data/raw/orders.csv

# Crawl 1 trang, lọc keyword "data"
./scripts/web_crawler.sh "https://news.ycombinator.com" "data" data/raw/hn

# Batch process tất cả CSV trong data/raw
./scripts/batch_process.sh

# Makefile
make help        # liệt kê lệnh
make check       # kiểm tra data
make pipeline    # crawl → process → check
```

## Yêu cầu

- Bash, `curl`, `awk`, `grep`, `sed`, `make` (sẵn trên Ubuntu/WSL2)
- `web_crawler.sh` cần mạng để fetch URL

> `lab_check.sh` kiểm tra theo các path `~/de-lab/...` như mô tả trong giáo trình — chạy sau khi đã dựng môi trường lab gốc, không phải trong repo này.
