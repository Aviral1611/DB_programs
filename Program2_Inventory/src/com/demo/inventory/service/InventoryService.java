package com.demo.inventory.service;

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
