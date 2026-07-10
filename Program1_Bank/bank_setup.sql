CREATE DATABASE IF NOT EXISTS demo_bank;
USE demo_bank;

CREATE TABLE IF NOT EXISTS accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    account_holder VARCHAR(100) NOT NULL,
    balance DECIMAL(15, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert some dummy data
INSERT INTO accounts (account_holder, balance) VALUES ('Alice', 5000.00);
INSERT INTO accounts (account_holder, balance) VALUES ('Bob', 3000.00);
INSERT INTO accounts (account_holder, balance) VALUES ('Charlie', 1500.50);
