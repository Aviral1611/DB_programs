package com.demo.inventory.dao;

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
