-- Run after creating the ecommerce_db database.
-- This DDL is the project's source of truth. For an existing database, inspect it first;
-- do not drop/recreate tables. Apply reviewed ALTER TABLE migrations when needed.

CREATE TABLE IF NOT EXISTS customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_contact VARCHAR(15) NOT NULL,
    customer_gender VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    product_image VARCHAR(500),
    product_name VARCHAR(150) NOT NULL,
    product_stock INTEGER NOT NULL DEFAULT 0,
    product_price NUMERIC(10,2) NOT NULL,
    CONSTRAINT ck_product_stock_nonnegative CHECK (product_stock >= 0),
    CONSTRAINT ck_product_price_nonnegative CHECK (product_price >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    order_datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_price NUMERIC(12,2) NOT NULL DEFAULT 0,
    discount NUMERIC(10,2) NOT NULL DEFAULT 0,
    customer_id INTEGER NOT NULL,
    CONSTRAINT fk_order_customer FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id) ON DELETE RESTRICT,
    CONSTRAINT ck_order_total_price_nonnegative CHECK (total_price >= 0),
    CONSTRAINT ck_order_discount_nonnegative CHECK (discount >= 0)
);

CREATE TABLE IF NOT EXISTS order_details (
    order_detail_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(12,2) NOT NULL,
    CONSTRAINT fk_detail_order FOREIGN KEY (order_id)
        REFERENCES orders(order_id) ON DELETE CASCADE,
    CONSTRAINT fk_detail_product FOREIGN KEY (product_id)
        REFERENCES products(product_id) ON DELETE RESTRICT,
    CONSTRAINT ck_detail_quantity_positive CHECK (quantity > 0),
    CONSTRAINT ck_detail_unit_price_nonnegative CHECK (unit_price >= 0),
    CONSTRAINT ck_detail_total_price_nonnegative CHECK (total_price >= 0)
);
