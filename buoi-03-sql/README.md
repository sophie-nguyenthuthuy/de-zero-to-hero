# Buổi 3 — Database & SQL (Lab)

Code lab cho [Buổi 3](../lessons/buoi-03-database-sql.md). Schema e-commerce + queries nâng cao + SQLAlchemy trên PostgreSQL.

## Cấu trúc

```
buoi-03-sql/
├── query_db.py            # Kết nối Python ↔ Postgres qua SQLAlchemy
└── sql/
    ├── 01_schema.sql       # DDL: customers / products / orders / order_items + indexes
    ├── 02_seed_data.sql    # Dữ liệu mẫu VN
    ├── 03_queries.sql      # JOIN, aggregation, window, CTE, cohort
    └── 04_performance.sql  # EXPLAIN ANALYZE, partial index, pg_stat
```

## Setup PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
sudo service postgresql start

sudo -u postgres psql << 'SQL'
CREATE USER deuser WITH PASSWORD 'depassword123';
CREATE DATABASE de_lab OWNER deuser;
GRANT ALL PRIVILEGES ON DATABASE de_lab TO deuser;
GRANT ALL ON SCHEMA public TO deuser;   -- cần cho PG15+
\q
SQL
```

> **PG15/16:** thiếu `GRANT ALL ON SCHEMA public TO deuser;` thì `01_schema.sql` báo `permission denied for schema public`.

## Chạy

```bash
cd buoi-03-sql
psql -h localhost -U deuser -d de_lab -W -f sql/01_schema.sql
psql -h localhost -U deuser -d de_lab -W -f sql/02_seed_data.sql
psql -h localhost -U deuser -d de_lab -W -f sql/03_queries.sql
psql -h localhost -U deuser -d de_lab -W -f sql/04_performance.sql

# Python ↔ Postgres
pip install sqlalchemy psycopg2-binary
python query_db.py
```

## Ghi chú

- `query_db.py` dùng password lab mặc định `depassword123` cho **localhost** — chỉ phục vụ học tập, đừng tái sử dụng ở môi trường thật.
- Các bug từ giáo trình gốc đã được sửa trong file `.sql` (streak CTE cast `interval`, tên cột `pg_stat_user_indexes`) — xem comment `LƯU Ý` trong file.
