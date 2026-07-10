package com.demo.inventory.main;

import com.demo.inventory.service.InventoryService;

public class InventoryMain {
    public static void main(String[] args) {
        System.out.println("=== E-Commerce Inventory Tracker ===");
        InventoryService inventoryService = new InventoryService();

        // 1. Show all products (uses JOIN)
        inventoryService.printAllProducts();
        
        // 2. Show total value (uses Aggregate SUM)
        inventoryService.printTotalValue();

        System.out.println("\n--- Processing Orders ---");
        // 3. Successful Checkout
        inventoryService.checkoutProduct(1, 2); // Buying 2 Laptops
        
        // 4. Failing Checkout (Exceeds stock)
        inventoryService.checkoutProduct(1, 20); // Buying 20 Laptops (Only 8 left)

        System.out.println("\n--- Final Inventory State ---");
        inventoryService.printAllProducts();
        inventoryService.printTotalValue();
    }
}
