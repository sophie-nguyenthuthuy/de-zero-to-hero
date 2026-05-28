# 🗄️ Buổi 3 — Database & SQL

**Data Engineer: Zero to Hero | Phase 1 – Engineering Foundations**
Thời gian: 2.5 tiếng | Lab: 60 phút

## 🎯 Mục tiêu Lab

- Setup PostgreSQL và DBeaver
- Thiết kế schema thực tế (e-commerce)
- Viết queries phức tạp: JOINs, Window Functions, CTEs
- Tối ưu query bằng Index + EXPLAIN ANALYZE
- Kết nối Python ↔ PostgreSQL qua SQLAlchemy

---

## PHẦN 1 — Cài đặt PostgreSQL (10 phút)

```bash
sudo apt install -y postgresql postgresql-contrib
sudo service postgresql start
sudo service postgresql status
sudo -u postgres psql -c "SELECT version();"

# Tạo user và database cho lab
sudo -u postgres psql << 'SQL'
CREATE USER deuser WITH PASSWORD 'depassword123';
CREATE DATABASE de_lab OWNER deuser;
GRANT ALL PRIVILEGES ON DATABASE de_lab TO deuser;
-- PG15+: cần cấp quyền schema public cho non-owner mới CREATE được bảng
GRANT ALL ON SCHEMA public TO deuser;
\q
SQL

psql -h localhost -U deuser -d de_lab -W   # password: depassword123
```

> **Gotcha PG15/16:** từ PostgreSQL 15, schema `public` không còn tự cấp `CREATE` cho mọi user, và `GRANT ALL ON DATABASE` không bao gồm quyền tạo bảng trong `public`. Nếu thiếu `GRANT ALL ON SCHEMA public TO deuser;` thì `\i sql/01_schema.sql` sẽ báo `permission denied for schema public`.

---

## PHẦN 2 — Schema Design & DDL (15 phút)

```bash
mkdir -p ~/de-lab/b03-sql/sql && cd ~/de-lab/b03-sql
psql -h localhost -U deuser -d de_lab -W -f sql/01_schema.sql
```

Schema e-commerce gồm 4 bảng — xem [`../buoi-03-sql/sql/01_schema.sql`](../buoi-03-sql/sql/01_schema.sql):

- **`customers`** — PK `customer_id` (CHECK `^C\d{3,}$`), email UNIQUE + CHECK regex, `is_active`, timestamps.
- **`products`** — SERIAL PK, `price`/`stock_qty` với CHECK ≥ 0.
- **`orders`** — FK → customers, `status` CHECK in (pending/processing/completed/cancelled/refunded), `total_amount` CHECK ≥ 0.
- **`order_items`** — FK → orders (ON DELETE CASCADE) & products, UNIQUE (order_id, product_id), `discount_pct` CHECK 0–100.

Extensions: `uuid-ossp`, `pg_trgm`. Index strategy: per-FK indexes, status/date indexes, và composite `idx_orders_customer_date (customer_id, order_date DESC)`.

---

## PHẦN 3 — DML: Insert dữ liệu mẫu (10 phút)

```bash
psql -h localhost -U deuser -d de_lab -W -f sql/02_seed_data.sql
```

Seed VN: 8 khách hàng (tên tiếng Việt, thành phố HN/HCM/ĐN/...), 10 sản phẩm (Electronics/Accessories/Fashion/Books, giá VND), 12 đơn hàng (tháng 1–3/2024), 17 order items. Xem [`../buoi-03-sql/sql/02_seed_data.sql`](../buoi-03-sql/sql/02_seed_data.sql).

---

## PHẦN 4 — SQL Queries (20 phút)

```bash
psql -h localhost -U deuser -d de_lab -W -f sql/03_queries.sql
```

[`../buoi-03-sql/sql/03_queries.sql`](../buoi-03-sql/sql/03_queries.sql) gồm:

1. **Basic SELECT + JOIN** — top 5 đơn completed lớn nhất.
2. **Aggregation** — doanh thu theo tháng với `DATE_TRUNC` + `LAG` (month-over-month change).
3. **Window functions** — `RANK`, pct-of-total, running total theo khách hàng.
4. **CTE** — tìm khách mua nhiều tháng liên tiếp (gaps-and-islands).
5. **Cohort analysis** — `first_order` + `AGE` để tính months-since-join.
6. **Product performance** — net revenue sau discount, `RANK` trong từng category.

> ⚠️ **Bug đã biết (query 4):** biểu thức `streak_group` cast `interval` sang `DATE` (`(... * INTERVAL '1 month')::DATE`) sẽ lỗi `cannot cast type interval to date`. Sửa: bỏ `::DATE`, dùng `order_month - (rn * INTERVAL '1 month')`.

---

## PHẦN 5 — EXPLAIN ANALYZE & Performance (10 phút)

```bash
psql -h localhost -U deuser -d de_lab -W -f sql/04_performance.sql
```

[`../buoi-03-sql/sql/04_performance.sql`](../buoi-03-sql/sql/04_performance.sql): `\timing on`, `EXPLAIN (ANALYZE, BUFFERS)` trước/sau index, partial index `idx_orders_completed_date` (WHERE status='completed'), `ANALYZE` cập nhật statistics, kiểm tra `pg_stat_user_indexes`, gợi ý `pg_stat_statements`.

> **Lưu ý 1:** `CREATE INDEX CONCURRENTLY` không chạy được trong transaction block. Khi chạy file qua `psql -f` ở chế độ autocommit thì OK; tránh bọc file trong `BEGIN/COMMIT` hoặc dùng `--single-transaction`.
>
> **Lưu ý 2 (bug đã sửa):** view `pg_stat_user_indexes` không có cột `tablename`/`indexname` — đúng tên là `relname` (bảng) và `indexrelname` (index). Bản gốc dùng `tablename`/`indexname` sẽ lỗi `column does not exist`; file `.sql` đã sửa sang `relname`/`indexrelname` (alias lại cho dễ đọc).

---

## PHẦN 6 — SQLAlchemy kết nối Python (5 phút)

```bash
pip install sqlalchemy psycopg2-binary
python query_db.py
```

[`../buoi-03-sql/query_db.py`](../buoi-03-sql/query_db.py): engine với connection pooling (`pool_pre_ping`), `query_to_dataframe()` qua `pd.read_sql`, và `run_transaction()` dùng `engine.begin()` (auto commit/rollback — ACID).

---

## 📚 Homework

1. Query tìm sản phẩm **chưa bao giờ** được đặt hàng (LEFT JOIN + IS NULL).
2. Tạo View `v_monthly_revenue` từ query doanh thu tháng.
3. Implement **SCD Type 2** cho bảng `products` khi giá thay đổi.

---

**Buổi tiếp theo:** Buổi 4 — Web API & FastAPI
