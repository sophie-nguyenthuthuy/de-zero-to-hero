# Data Engineer: Zero to Hero

Khóa học Data Engineering thực chiến, đi từ nền tảng kỹ thuật đến pipeline production. Mỗi buổi gồm phần lý thuyết (~2.5 tiếng) và một **Lab** thực hành (~60 phút) với code chạy được, dữ liệu mẫu kiểu Việt Nam (VND, tên tiếng Việt) và bài tập về nhà.

## Phase 1 — Engineering Foundations

| Buổi | Chủ đề | Lab chính | Thư mục |
|------|--------|-----------|---------|
| [Buổi 1](lessons/buoi-01-linux-shell.md) | Linux, Shell & Dev Environment | CLI Web Crawler bằng Bash | [`buoi-01-linux/`](buoi-01-linux/) |
| [Buổi 2](lessons/buoi-02-python-etl.md) | Python cho Data Engineering | ETL Pipeline (Extract → Transform → Load) | [`buoi-02-python/`](buoi-02-python/) |
| [Buổi 3](lessons/buoi-03-database-sql.md) | Database & SQL | Schema e-commerce + queries nâng cao + SQLAlchemy | [`buoi-03-sql/`](buoi-03-sql/) |
| Buổi 4 | Web API & FastAPI | _(sắp ra mắt)_ | — |

## Cấu trúc repo

```
de-zero-to-hero/
├── lessons/                # Giáo trình từng buổi (Markdown, tiếng Việt)
├── buoi-01-linux/          # Lab Bash: web crawler, data quality, Makefile
├── buoi-02-python/         # Lab Python: ETL package + CLI (uv project)
└── buoi-03-sql/            # Lab SQL: DDL/DML, queries, SQLAlchemy
```

## Cách dùng

Mỗi thư mục lab tự chứa (self-contained). Đọc file giáo trình tương ứng trong `lessons/` trước, rồi chạy code trong thư mục lab của buổi đó. Hướng dẫn cài đặt cụ thể (WSL2/Ubuntu, `uv`, PostgreSQL...) nằm ngay trong từng bài.

## Yêu cầu chung

- Ubuntu (WSL2) hoặc EC2 Ubuntu
- Python 3.10+
- Các tool cài thêm theo từng buổi (xem giáo trình)

## License

[MIT](LICENSE) — tự do dùng cho học tập và giảng dạy.
