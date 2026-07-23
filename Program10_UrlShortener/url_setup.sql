CREATE DATABASE IF NOT EXISTS demo_urlshortener;
USE demo_urlshortener;

CREATE TABLE IF NOT EXISTS short_urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL UNIQUE,
    original_url TEXT NOT NULL,
    click_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
