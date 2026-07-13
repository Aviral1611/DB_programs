import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    # Program 3: Employee
    "Program3_Employee/employee_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_employee;
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
""",
    
    "Program3_Employee/src/com/demo/employee/db/DatabaseConnection.java": """package com.demo.employee.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_employee";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",
    
    "Program3_Employee/src/com/demo/employee/model/Employee.java": """package com.demo.employee.model;

public class Employee {
    private int employeeId;
    private String name;
    private double salary;
    private int departmentId;

    public Employee(int employeeId, String name, double salary, int departmentId) {
        this.employeeId = employeeId;
        this.name = name;
        this.salary = salary;
        this.departmentId = departmentId;
    }

    @Override
    public String toString() {
        return "Employee [ID=" + employeeId + ", Name=" + name + ", Salary=$" + salary + ", DeptID=" + departmentId + "]";
    }
}
""",
    
    "Program3_Employee/src/com/demo/employee/dao/EmployeeDAO.java": """package com.demo.employee.dao;

import com.demo.employee.model.Employee;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class EmployeeDAO {
    public List<Employee> getEmployeesByDepartment(Connection conn, int departmentId) throws SQLException {
        List<Employee> employees = new ArrayList<>();
        String sql = "SELECT * FROM employees WHERE department_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, departmentId);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    employees.add(new Employee(
                        rs.getInt("employee_id"),
                        rs.getString("name"),
                        rs.getDouble("salary"),
                        rs.getInt("department_id")
                    ));
                }
            }
        }
        return employees;
    }

    public void giveBonusToDepartment(Connection conn, int departmentId, double bonusPercentage) throws SQLException {
        String sql = "UPDATE employees SET salary = salary + (salary * ?) WHERE department_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, bonusPercentage / 100.0);
            pstmt.setInt(2, departmentId);
            pstmt.executeUpdate();
        }
    }
}
""",
    
    "Program3_Employee/src/com/demo/employee/service/EmployeeService.java": """package com.demo.employee.service;

import com.demo.employee.dao.EmployeeDAO;
import com.demo.employee.db.DatabaseConnection;
import com.demo.employee.model.Employee;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

public class EmployeeService {
    private EmployeeDAO employeeDAO = new EmployeeDAO();

    public void printEmployeesInDepartment(int departmentId) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            List<Employee> employees = employeeDAO.getEmployeesByDepartment(conn, departmentId);
            System.out.println("Employees in Department " + departmentId + ":");
            for (Employee e : employees) {
                System.out.println(e);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void applyBonus(int departmentId, double bonusPercentage) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            employeeDAO.giveBonusToDepartment(conn, departmentId, bonusPercentage);
            System.out.println("Applied " + bonusPercentage + "% bonus to Department " + departmentId);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
""",
    
    "Program3_Employee/src/com/demo/employee/main/EmployeeMain.java": """package com.demo.employee.main;

import com.demo.employee.service.EmployeeService;

public class EmployeeMain {
    public static void main(String[] args) {
        System.out.println("=== Employee Management System ===");
        EmployeeService service = new EmployeeService();

        int engineeringDeptId = 2;
        System.out.println("\\n[Before Bonus]");
        service.printEmployeesInDepartment(engineeringDeptId);

        service.applyBonus(engineeringDeptId, 10.0); // 10% bonus

        System.out.println("\\n[After Bonus]");
        service.printEmployeesInDepartment(engineeringDeptId);
    }
}
""",
    
    # Program 4: Library
    "Program4_Library/library_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_library;
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
""",

    "Program4_Library/src/com/demo/library/db/DatabaseConnection.java": """package com.demo.library.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_library";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program4_Library/src/com/demo/library/model/Book.java": """package com.demo.library.model;

public class Book {
    private int bookId;
    private String title;
    private int availableCopies;

    public Book(int bookId, String title, int availableCopies) {
        this.bookId = bookId;
        this.title = title;
        this.availableCopies = availableCopies;
    }

    @Override
    public String toString() {
        return "Book [ID=" + bookId + ", Title='" + title + "', Available=" + availableCopies + "]";
    }
}
""",

    "Program4_Library/src/com/demo/library/dao/LibraryDAO.java": """package com.demo.library.dao;

import com.demo.library.model.Book;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class LibraryDAO {
    public Book getBookById(Connection conn, int bookId) throws SQLException {
        String sql = "SELECT * FROM books WHERE book_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, bookId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return new Book(rs.getInt("book_id"), rs.getString("title"), rs.getInt("available_copies"));
                }
            }
        }
        return null;
    }

    public boolean checkoutBook(Connection conn, int bookId, String memberName) throws SQLException {
        String updateBookSql = "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ? AND available_copies > 0";
        String insertCheckoutSql = "INSERT INTO checkouts (book_id, member_name) VALUES (?, ?)";

        try (PreparedStatement updateStmt = conn.prepareStatement(updateBookSql)) {
            updateStmt.setInt(1, bookId);
            int rowsAffected = updateStmt.executeUpdate();
            
            if (rowsAffected > 0) {
                try (PreparedStatement insertStmt = conn.prepareStatement(insertCheckoutSql)) {
                    insertStmt.setInt(1, bookId);
                    insertStmt.setString(2, memberName);
                    insertStmt.executeUpdate();
                }
                return true;
            }
        }
        return false;
    }
}
""",

    "Program4_Library/src/com/demo/library/service/LibraryService.java": """package com.demo.library.service;

import com.demo.library.dao.LibraryDAO;
import com.demo.library.db.DatabaseConnection;
import com.demo.library.model.Book;
import java.sql.Connection;
import java.sql.SQLException;

public class LibraryService {
    private LibraryDAO libraryDAO = new LibraryDAO();

    public void displayBookStatus(int bookId) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            Book book = libraryDAO.getBookById(conn, bookId);
            if (book != null) {
                System.out.println(book);
            } else {
                System.out.println("Book not found.");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void borrowBook(int bookId, String memberName) {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            conn.setAutoCommit(false);

            boolean success = libraryDAO.checkoutBook(conn, bookId, memberName);
            if (success) {
                conn.commit();
                System.out.println(memberName + " successfully borrowed Book ID " + bookId);
            } else {
                conn.rollback();
                System.out.println("Checkout failed for Book ID " + bookId + ". No copies available.");
            }
        } catch (SQLException e) {
            if (conn != null) {
                try { conn.rollback(); } catch (SQLException ex) { ex.printStackTrace(); }
            }
            e.printStackTrace();
        } finally {
            if (conn != null) {
                try {
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
""",

    "Program4_Library/src/com/demo/library/main/LibraryMain.java": """package com.demo.library.main;

import com.demo.library.service.LibraryService;

public class LibraryMain {
    public static void main(String[] args) {
        System.out.println("=== Library Book Checkout System ===");
        LibraryService service = new LibraryService();

        int book1984Id = 2; // 1 copy available
        int bookMockingbirdId = 3; // 0 copies available

        System.out.println("\\n[Status Before Checkout]");
        service.displayBookStatus(book1984Id);
        service.displayBookStatus(bookMockingbirdId);

        System.out.println("\\n[Attempting Checkouts]");
        service.borrowBook(book1984Id, "Alice");
        service.borrowBook(book1984Id, "Bob"); // Should fail, only 1 copy
        service.borrowBook(bookMockingbirdId, "Charlie"); // Should fail, 0 copies

        System.out.println("\\n[Status After Checkout]");
        service.displayBookStatus(book1984Id);
        service.displayBookStatus(bookMockingbirdId);
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Programs 3 and 4 generated successfully!")
