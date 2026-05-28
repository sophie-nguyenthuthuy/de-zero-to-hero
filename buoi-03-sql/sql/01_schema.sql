-- ============================================
-- E-COMMERCE SCHEMA
-- Chạy trong psql: \i sql/01_schema.sql
-- ============================================

-- Bật extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- Cho full-text search

-- ===== CUSTOMERS =====
CREATE TABLE IF NOT EXISTS customers (
    customer_id   VARCHAR(20)  PRIMARY KEY,
    full_name     VARCHAR(200) NOT NULL,
    email         VARCHAR(200) UNIQUE NOT NULL,
    phone         VARCHAR(20),
    city          VARCHAR(100),
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_customer_id CHECK (customer_id ~ '^C\d{3,}$'),
    CONSTRAINT chk_email CHECK (email ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$')
);

-- ===== PRODUCTS =====
CREATE TABLE IF NOT EXISTS products (
    product_id    SERIAL        PRIMARY KEY,
    product_name  VARCHAR(200)  NOT NULL,
    category      VARCHAR(100)  NOT NULL,
    price         NUMERIC(15,2) NOT NULL CHECK (price >= 0),
    stock_qty     INTEGER       NOT NULL DEFAULT 0 CHECK (stock_qty >= 0),
    created_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ===== ORDERS =====
CREATE TABLE IF NOT EXISTS orders (
    order_id       SERIAL        PRIMARY KEY,
    customer_id    VARCHAR(20)   NOT NULL REFERENCES customers(customer_id),
    order_date     DATE          NOT NULL DEFAULT CURRENT_DATE,
    status         VARCHAR(20)   NOT NULL DEFAULT 'pending'
                                 CHECK (status IN ('pending','processing','completed','cancelled','refunded')),
    total_amount   NUMERIC(15,2) NOT NULL CHECK (total_amount >= 0),
    payment_method VARCHAR(50),
    created_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ===== ORDER ITEMS =====
CREATE TABLE IF NOT EXISTS order_items (
    item_id       SERIAL        PRIMARY KEY,
    order_id      INTEGER       NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id    INTEGER       NOT NULL REFERENCES products(product_id),
    quantity      INTEGER       NOT NULL CHECK (quantity > 0),
    unit_price    NUMERIC(15,2) NOT NULL CHECK (unit_price >= 0),
    discount_pct  NUMERIC(5,2)  NOT NULL DEFAULT 0 CHECK (discount_pct BETWEEN 0 AND 100),

    CONSTRAINT uq_order_product UNIQUE (order_id, product_id)
);

-- ===== INDEXES =====
CREATE INDEX IF NOT EXISTS idx_orders_customer_id   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date          ON orders(order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status        ON orders(status);
CREATE INDEX IF NOT EXISTS idx_order_items_order    ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product  ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_customers_email      ON customers(email);

-- Composite index cho query phổ biến
CREATE INDEX IF NOT EXISTS idx_orders_customer_date ON orders(customer_id, order_date DESC);
