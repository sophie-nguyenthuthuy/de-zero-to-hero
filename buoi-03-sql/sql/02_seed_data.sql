-- ============================================
-- SEED DATA — Dữ liệu mẫu cho Lab
-- ============================================

-- Customers
INSERT INTO customers (customer_id, full_name, email, phone, city) VALUES
('C001', 'Nguyễn Văn An',    'an.nguyen@email.com',    '0912345678', 'Hà Nội'),
('C002', 'Trần Thị Bình',    'binh.tran@email.com',    '0987654321', 'HCM'),
('C003', 'Lê Văn Cường',     'cuong.le@email.com',     '0901234567', 'Đà Nẵng'),
('C004', 'Phạm Thị Dung',    'dung.pham@email.com',    '0934567890', 'Hà Nội'),
('C005', 'Hoàng Văn Em',     'em.hoang@email.com',     '0923456789', 'HCM'),
('C006', 'Võ Thị Phương',    'phuong.vo@email.com',    NULL,         'Cần Thơ'),
('C007', 'Đặng Văn Giang',   'giang.dang@email.com',   '0956789012', 'Hải Phòng'),
('C008', 'Bùi Thị Hoa',      'hoa.bui@email.com',      '0945678901', 'HCM')
ON CONFLICT DO NOTHING;

-- Products
INSERT INTO products (product_name, category, price, stock_qty) VALUES
('Laptop Dell XPS 15',       'Electronics', 28000000, 50),
('iPhone 15 Pro',            'Electronics', 29000000, 100),
('Samsung Galaxy S24',       'Electronics', 22000000, 75),
('Tai nghe Sony WH-1000XM5', 'Electronics',  8500000, 200),
('Màn hình LG 27"',          'Electronics',  7000000, 30),
('Bàn phím Keychron K2',     'Accessories',  2800000, 150),
('Chuột Logitech MX Master', 'Accessories',  2500000, 120),
('Áo phông unisex',          'Fashion',       350000, 500),
('Quần jean slim',           'Fashion',      1200000, 300),
('Sách "Clean Code"',        'Books',         450000, 80);

-- Orders (tháng 1-3/2024)
INSERT INTO orders (customer_id, order_date, status, total_amount, payment_method) VALUES
('C001', '2024-01-15', 'completed', 29000000, 'credit_card'),
('C002', '2024-01-16', 'completed',  8500000, 'e_wallet'),
('C003', '2024-01-20', 'completed', 28000000, 'bank_transfer'),
('C001', '2024-02-01', 'completed',  2800000, 'credit_card'),
('C004', '2024-02-10', 'completed', 22000000, 'credit_card'),
('C005', '2024-02-14', 'cancelled',  7000000, 'e_wallet'),
('C002', '2024-02-20', 'completed',  3700000, 'e_wallet'),
('C006', '2024-03-01', 'completed', 29000000, 'bank_transfer'),
('C007', '2024-03-05', 'processing',  800000, 'e_wallet'),
('C001', '2024-03-10', 'completed', 31800000, 'credit_card'),
('C008', '2024-03-15', 'completed', 22350000, 'credit_card'),
('C003', '2024-03-20', 'refunded',   8500000, 'credit_card');

-- Order Items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, discount_pct) VALUES
(1,  2, 1, 29000000, 0),    -- iPhone
(2,  4, 1,  8500000, 0),    -- Sony headphones
(3,  1, 1, 28000000, 0),    -- Dell Laptop
(4,  6, 1,  2800000, 0),    -- Keyboard
(5,  3, 1, 22000000, 0),    -- Samsung
(6,  5, 1,  7000000, 0),    -- Monitor (cancelled)
(7,  7, 1,  2500000, 0),    -- Mouse
(7,  6, 1,  2800000, 10),   -- Keyboard 10% off  (same order C002)
(8,  2, 1, 29000000, 0),    -- iPhone
(9,  8, 2,   350000, 0),    -- Áo x2
(9, 10, 1,   450000, 0),    -- Sách
(10, 1, 1, 28000000, 0),    -- Dell Laptop
(10, 4, 1,  8500000, 0),    -- Sony headphones
(10, 6, 1,  2800000, 0),    -- Keyboard
(11, 3, 1, 22000000, 5),    -- Samsung 5% off
(11, 7, 1,  2500000, 0),    -- Mouse
(12, 4, 1,  8500000, 0);    -- Sony (refunded)
