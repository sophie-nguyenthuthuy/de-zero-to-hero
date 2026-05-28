-- ============================================
-- SQL QUERIES LAB — B03
-- Chạy từng phần để hiểu kết quả
-- ============================================

-- ===== 1. BASIC SELECT & FILTERING =====
-- Top 5 đơn hàng lớn nhất
SELECT
    o.order_id,
    c.full_name,
    o.order_date,
    o.total_amount,
    o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'completed'
ORDER BY o.total_amount DESC
LIMIT 5;


-- ===== 2. AGGREGATION =====
-- Doanh thu theo tháng (kèm month-over-month change qua LAG)
SELECT
    DATE_TRUNC('month', order_date) AS month,
    COUNT(*) AS order_count,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(total_amount) AS revenue,
    AVG(total_amount)::NUMERIC(15,2) AS avg_order_value,
    SUM(total_amount) - LAG(SUM(total_amount))
        OVER (ORDER BY DATE_TRUNC('month', order_date)) AS mom_change
FROM orders
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;


-- ===== 3. WINDOW FUNCTIONS =====
-- Rank khách hàng theo doanh thu, kèm running total
SELECT
    c.customer_id,
    c.full_name,
    c.city,
    COUNT(o.order_id) AS order_count,
    SUM(o.total_amount) AS total_spent,
    RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS revenue_rank,
    ROUND(
        SUM(o.total_amount) * 100.0 / SUM(SUM(o.total_amount)) OVER (),
        2
    ) AS pct_of_total,
    SUM(SUM(o.total_amount)) OVER (ORDER BY SUM(o.total_amount) DESC) AS running_total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.status = 'completed'
GROUP BY c.customer_id, c.full_name, c.city
ORDER BY revenue_rank;


-- ===== 4. CTE — Common Table Expressions =====
-- Tìm khách hàng mua hàng nhiều tháng liên tiếp (gaps-and-islands)
-- LƯU Ý: bản gốc dùng (rn * INTERVAL '1 month')::DATE — Postgres KHÔNG cho cast
--        interval -> date (lỗi "cannot cast type interval to date"). Đã bỏ ::DATE;
--        date - interval trả về timestamp, GROUP BY vẫn đúng.
WITH monthly_orders AS (
    SELECT
        customer_id,
        DATE_TRUNC('month', order_date)::DATE AS order_month,
        COUNT(*) AS orders_in_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id, DATE_TRUNC('month', order_date)
),
customer_streaks AS (
    SELECT
        customer_id,
        order_month,
        orders_in_month,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_month) AS rn,
        order_month - (ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_month)
                       * INTERVAL '1 month') AS streak_group
    FROM monthly_orders
),
streak_lengths AS (
    SELECT
        customer_id,
        COUNT(*) AS consecutive_months,
        MIN(order_month) AS streak_start,
        MAX(order_month) AS streak_end
    FROM customer_streaks
    GROUP BY customer_id, streak_group
)
SELECT
    c.customer_id,
    c.full_name,
    s.consecutive_months,
    s.streak_start,
    s.streak_end
FROM streak_lengths s
JOIN customers c ON s.customer_id = c.customer_id
WHERE s.consecutive_months >= 2
ORDER BY s.consecutive_months DESC;


-- ===== 5. ADVANCED: Cohort Analysis =====
WITH first_order AS (
    SELECT
        customer_id,
        MIN(DATE_TRUNC('month', order_date)) AS cohort_month
    FROM orders
    WHERE status = 'completed'
    GROUP BY customer_id
),
order_activity AS (
    SELECT
        o.customer_id,
        DATE_TRUNC('month', o.order_date) AS order_month,
        f.cohort_month,
        EXTRACT(MONTH FROM AGE(DATE_TRUNC('month', o.order_date), f.cohort_month))
            AS months_since_join
    FROM orders o
    JOIN first_order f ON o.customer_id = f.customer_id
    WHERE o.status = 'completed'
)
SELECT
    cohort_month,
    months_since_join,
    COUNT(DISTINCT customer_id) AS active_customers
FROM order_activity
GROUP BY cohort_month, months_since_join
ORDER BY cohort_month, months_since_join;


-- ===== 6. PRODUCT PERFORMANCE =====
SELECT
    p.category,
    p.product_name,
    SUM(oi.quantity) AS total_sold,
    SUM(oi.quantity * oi.unit_price * (1 - oi.discount_pct / 100)) AS net_revenue,
    AVG(oi.discount_pct) AS avg_discount,
    COUNT(DISTINCT oi.order_id) AS order_count,
    RANK() OVER (
        PARTITION BY p.category
        ORDER BY SUM(oi.quantity * oi.unit_price) DESC
    ) AS rank_in_category
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status IN ('completed', 'processing')
GROUP BY p.category, p.product_name, p.product_id
ORDER BY p.category, rank_in_category;
