-- ============================================
-- QUERY PERFORMANCE — EXPLAIN ANALYZE
-- ============================================

-- Bật timing
\timing on

-- ===== 1. Query không có index (xấu) =====
-- Tìm đơn hàng theo khoảng ngày
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE order_date BETWEEN '2024-01-01' AND '2024-03-31';

-- ===== 2. Thêm index và so sánh =====
-- Partial index cho completed orders (query phổ biến nhất)
-- LƯU Ý: CREATE INDEX CONCURRENTLY không chạy được trong transaction block.
--        Khi chạy file qua `psql -f` (autocommit) thì OK; tránh bọc trong BEGIN/COMMIT.
CREATE INDEX CONCURRENTLY IF NOT EXISTS
    idx_orders_completed_date
ON orders(order_date)
WHERE status = 'completed';

-- Query với index
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders
WHERE status = 'completed'
  AND order_date BETWEEN '2024-01-01' AND '2024-03-31';

-- ===== 3. ANALYZE TABLE (cập nhật statistics) =====
ANALYZE orders;
ANALYZE order_items;

-- ===== 4. Kiểm tra index usage =====
SELECT
    schemaname,
    relname     AS tablename,
    indexrelname AS indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE relname IN ('orders', 'order_items', 'customers')
ORDER BY relname, indexrelname;

-- ===== 5. Tìm slow queries =====
-- (Cần bật pg_stat_statements extension)
-- CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
-- SELECT query, calls, mean_exec_time, rows
-- FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;
