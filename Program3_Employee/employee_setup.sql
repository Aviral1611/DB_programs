CREATE DATABASE IF NOT EXISTS demo_employee;
USE demo_employee;

CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

INSERT INTO departments (name) VALUES ('HR'), ('Engineering'), ('Sales');
INSERT INTO employees (name, salary, department_id) VALUES 
('David', 60000.00, 1),
('Eve', 80000.00, 2),
('Frank', 90000.00, 2),
('Grace', 75000.00, 3);
