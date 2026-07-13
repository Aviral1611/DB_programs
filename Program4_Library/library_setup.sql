CREATE DATABASE IF NOT EXISTS demo_library;
USE demo_library;

CREATE TABLE IF NOT EXISTS books (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    available_copies INT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkouts (
    checkout_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT,
    member_name VARCHAR(100) NOT NULL,
    checkout_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(book_id)
);

INSERT INTO books (title, available_copies) VALUES 
('The Great Gatsby', 3),
('1984', 1),
('To Kill a Mockingbird', 0);
