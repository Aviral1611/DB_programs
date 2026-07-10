package com.demo.inventory.model;

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
