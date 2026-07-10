CREATE DATABASE IF NOT EXISTS demo_inventory;
USE demo_inventory;

CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INT NOT NULL,
    category_id INT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Insert dummy data
INSERT INTO categories (name) VALUES ('Electronics'), ('Books');

INSERT INTO products (name, price, stock_quantity, category_id) VALUES 
('Laptop', 1200.00, 10, 1),
('Smartphone', 800.00, 50, 1),
('Java Programming Book', 45.00, 25, 2);
