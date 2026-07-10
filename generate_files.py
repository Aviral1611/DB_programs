import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    # Program 1: Bank
    "Program1_Bank/bank_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_bank;
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
""",
    
    "Program1_Bank/src/com/demo/bank/db/DatabaseConnection.java": """package com.demo.bank.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    // Update these credentials according to your MySQL Workbench setup
    private static final String URL = "jdbc:mysql://localhost:3306/demo_bank";
    private static final String USER = "root";
    private static final String PASSWORD = "root"; // change if needed

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program1_Bank/src/com/demo/bank/model/Account.java": """package com.demo.bank.model;

public class Account {
    private int accountId;
    private String accountHolder;
    private double balance;

    public Account() {}

    public Account(int accountId, String accountHolder, double balance) {
        this.accountId = accountId;
        this.accountHolder = accountHolder;
        this.balance = balance;
    }

    public int getAccountId() { return accountId; }
    public void setAccountId(int accountId) { this.accountId = accountId; }

    public String getAccountHolder() { return accountHolder; }
    public void setAccountHolder(String accountHolder) { this.accountHolder = accountHolder; }

    public double getBalance() { return balance; }
    public void setBalance(double balance) { this.balance = balance; }

    @Override
    public String toString() {
        return "Account [ID=" + accountId + ", Holder=" + accountHolder + ", Balance=$" + balance + "]";
    }
}
""",

    "Program1_Bank/src/com/demo/bank/dao/AccountDAO.java": """package com.demo.bank.dao;

import com.demo.bank.model.Account;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class AccountDAO {
    
    public Account getAccountById(Connection conn, int accountId) throws SQLException {
        String sql = "SELECT * FROM accounts WHERE account_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, accountId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return new Account(
                        rs.getInt("account_id"),
                        rs.getString("account_holder"),
                        rs.getDouble("balance")
                    );
                }
            }
        }
        return null;
    }

    public void updateBalance(Connection conn, int accountId, double newBalance) throws SQLException {
        String sql = "UPDATE accounts SET balance = ? WHERE account_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, newBalance);
            pstmt.setInt(2, accountId);
            pstmt.executeUpdate();
        }
    }
}
""",

    "Program1_Bank/src/com/demo/bank/service/BankService.java": """package com.demo.bank.service;

import com.demo.bank.dao.AccountDAO;
import com.demo.bank.db.DatabaseConnection;
import com.demo.bank.model.Account;

import java.sql.Connection;
import java.sql.SQLException;

public class BankService {
    private AccountDAO accountDAO;

    public BankService() {
        this.accountDAO = new AccountDAO();
    }

    /**
     * Demonstrates a transaction using ACID properties.
     * We disable auto-commit, perform two updates, and then commit.
     * If anything fails, we rollback the entire transaction.
     */
    public boolean transferFunds(int fromAccountId, int toAccountId, double amount) {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            // Start transaction
            conn.setAutoCommit(false);
            System.out.println("Transaction started...");

            Account fromAccount = accountDAO.getAccountById(conn, fromAccountId);
            Account toAccount = accountDAO.getAccountById(conn, toAccountId);

            if (fromAccount == null || toAccount == null) {
                System.out.println("One or both accounts do not exist. Transfer failed.");
                conn.rollback();
                return false;
            }

            if (fromAccount.getBalance() < amount) {
                System.out.println("Insufficient funds in Account " + fromAccountId + ". Transfer failed.");
                conn.rollback();
                return false;
            }

            // Deduct from sender
            double newFromBalance = fromAccount.getBalance() - amount;
            accountDAO.updateBalance(conn, fromAccountId, newFromBalance);
            
            // Add to receiver
            double newToBalance = toAccount.getBalance() + amount;
            accountDAO.updateBalance(conn, toAccountId, newToBalance);

            // Commit transaction
            conn.commit();
            System.out.println("Transfer of $" + amount + " successful! Transaction committed.");
            return true;

        } catch (SQLException e) {
            System.err.println("SQL Error occurred. Rolling back transaction...");
            if (conn != null) {
                try {
                    conn.rollback();
                } catch (SQLException ex) {
                    ex.printStackTrace();
                }
            }
            e.printStackTrace();
            return false;
        } finally {
            if (conn != null) {
                try {
                    // Reset auto-commit and close connection
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }
    }
    
    public void printAccountDetails(int accountId) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            Account acc = accountDAO.getAccountById(conn, accountId);
            if (acc != null) {
                System.out.println(acc);
            } else {
                System.out.println("Account " + accountId + " not found.");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
""",

    "Program1_Bank/src/com/demo/bank/main/BankMain.java": """package com.demo.bank.main;

import com.demo.bank.service.BankService;

public class BankMain {
    public static void main(String[] args) {
        System.out.println("--- Bank Transaction Manager ---");
        BankService bankService = new BankService();

        int aliceId = 1;
        int bobId = 2;

        System.out.println("\\n[Before Transfer]");
        bankService.printAccountDetails(aliceId);
        bankService.printAccountDetails(bobId);

        System.out.println("\\n[Initiating Transfer: Alice to Bob - $500]");
        boolean success = bankService.transferFunds(aliceId, bobId, 500.0);

        if (success) {
            System.out.println("\\n[After Successful Transfer]");
            bankService.printAccountDetails(aliceId);
            bankService.printAccountDetails(bobId);
        }

        System.out.println("\\n[Initiating Failing Transfer: Bob to Alice - $10000 (Insufficient Funds)]");
        bankService.transferFunds(bobId, aliceId, 10000.0);
        
        System.out.println("\\n[After Failed Transfer (Values should remain unchanged)]");
        bankService.printAccountDetails(aliceId);
        bankService.printAccountDetails(bobId);
    }
}
""",

    # Program 2: Inventory
    "Program2_Inventory/inventory_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_inventory;
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
""",

    "Program2_Inventory/src/com/demo/inventory/db/DatabaseConnection.java": """package com.demo.inventory.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_inventory";
    private static final String USER = "root";
    private static final String PASSWORD = "root"; // change if needed

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program2_Inventory/src/com/demo/inventory/model/Category.java": """package com.demo.inventory.model;

public class Category {
    private int categoryId;
    private String name;

    public Category(int categoryId, String name) {
        this.categoryId = categoryId;
        this.name = name;
    }

    public int getCategoryId() { return categoryId; }
    public String getName() { return name; }
    
    @Override
    public String toString() {
        return name;
    }
}
""",

    "Program2_Inventory/src/com/demo/inventory/model/Product.java": """package com.demo.inventory.model;

public class Product {
    private int productId;
    private String name;
    private double price;
    private int stockQuantity;
    private Category category;

    public Product(int productId, String name, double price, int stockQuantity, Category category) {
        this.productId = productId;
        this.name = name;
        this.price = price;
        this.stockQuantity = stockQuantity;
        this.category = category;
    }

    public int getProductId() { return productId; }
    public String getName() { return name; }
    public double getPrice() { return price; }
    public int getStockQuantity() { return stockQuantity; }
    public Category getCategory() { return category; }

    @Override
    public String toString() {
        return "Product [ID=" + productId + ", Name=" + name + ", Price=$" + price + 
               ", Stock=" + stockQuantity + ", Category=" + (category != null ? category.getName() : "None") + "]";
    }
}
""",

    "Program2_Inventory/src/com/demo/inventory/dao/InventoryDAO.java": """package com.demo.inventory.dao;

import com.demo.inventory.model.Category;
import com.demo.inventory.model.Product;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class InventoryDAO {

    // Demonstrates a JOIN query
    public List<Product> getAllProducts(Connection conn) throws SQLException {
        List<Product> products = new ArrayList<>();
        String sql = "SELECT p.*, c.name as category_name " +
                     "FROM products p " +
                     "LEFT JOIN categories c ON p.category_id = c.category_id";
                     
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
             
            while (rs.next()) {
                Category cat = new Category(rs.getInt("category_id"), rs.getString("category_name"));
                Product prod = new Product(
                    rs.getInt("product_id"),
                    rs.getString("name"),
                    rs.getDouble("price"),
                    rs.getInt("stock_quantity"),
                    cat
                );
                products.add(prod);
            }
        }
        return products;
    }

    public boolean reduceStock(Connection conn, int productId, int quantity) throws SQLException {
        // Only update if there is enough stock
        String sql = "UPDATE products SET stock_quantity = stock_quantity - ? " +
                     "WHERE product_id = ? AND stock_quantity >= ?";
                     
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, quantity);
            pstmt.setInt(2, productId);
            pstmt.setInt(3, quantity);
            
            int affectedRows = pstmt.executeUpdate();
            return affectedRows > 0; // true if successful, false if not enough stock or product not found
        }
    }
    
    public double getTotalInventoryValue(Connection conn) throws SQLException {
        String sql = "SELECT SUM(price * stock_quantity) as total_value FROM products";
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
             
            if (rs.next()) {
                return rs.getDouble("total_value");
            }
        }
        return 0.0;
    }
}
""",

    "Program2_Inventory/src/com/demo/inventory/service/InventoryService.java": """package com.demo.inventory.service;

import com.demo.inventory.dao.InventoryDAO;
import com.demo.inventory.db.DatabaseConnection;
import com.demo.inventory.model.Product;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

public class InventoryService {
    private InventoryDAO inventoryDAO;

    public InventoryService() {
        this.inventoryDAO = new InventoryDAO();
    }

    public void printAllProducts() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            List<Product> products = inventoryDAO.getAllProducts(conn);
            System.out.println("--- Current Inventory ---");
            for (Product p : products) {
                System.out.println(p);
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void checkoutProduct(int productId, int quantity) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            System.out.println("Attempting to checkout " + quantity + " units of Product ID " + productId + "...");
            boolean success = inventoryDAO.reduceStock(conn, productId, quantity);
            
            if (success) {
                System.out.println("Checkout successful!");
            } else {
                System.out.println("Checkout failed! Not enough stock or product does not exist.");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
    
    public void printTotalValue() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            double total = inventoryDAO.getTotalInventoryValue(conn);
            System.out.println("Total Inventory Value: $" + total);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
""",

    "Program2_Inventory/src/com/demo/inventory/main/InventoryMain.java": """package com.demo.inventory.main;

import com.demo.inventory.service.InventoryService;

public class InventoryMain {
    public static void main(String[] args) {
        System.out.println("=== E-Commerce Inventory Tracker ===");
        InventoryService inventoryService = new InventoryService();

        // 1. Show all products (uses JOIN)
        inventoryService.printAllProducts();
        
        // 2. Show total value (uses Aggregate SUM)
        inventoryService.printTotalValue();

        System.out.println("\\n--- Processing Orders ---");
        // 3. Successful Checkout
        inventoryService.checkoutProduct(1, 2); // Buying 2 Laptops
        
        // 4. Failing Checkout (Exceeds stock)
        inventoryService.checkoutProduct(1, 20); // Buying 20 Laptops (Only 8 left)

        System.out.println("\\n--- Final Inventory State ---");
        inventoryService.printAllProducts();
        inventoryService.printTotalValue();
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("All files generated successfully!")
