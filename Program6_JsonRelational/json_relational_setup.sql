CREATE DATABASE IF NOT EXISTS demo_jsonrel;
USE demo_jsonrel;

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_hobbies (
    hobby_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    hobby VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
