package com.demo.apicache.main;

import com.demo.apicache.service.ApiService;

public class ApiCacheMain {
    public static void main(String[] args) {
        System.out.println("=== API Caching System (L1 + L2 Architecture) ===");
        ApiService service = new ApiService();
        String apiUrl = "https://api.agify.io?name=java";

        System.out.println("\n[Request 1 - Cold Start]");
        String result1 = service.getData(apiUrl);
        System.out.println("Result: " + result1);

        System.out.println("\n[Request 2 - Immediate Follow-up]");
        String result2 = service.getData(apiUrl);
        System.out.println("Result: " + result2);
        
        System.out.println("\n--- Simulating Application Restart ---");
        System.out.println("Destroying old Service (and its L1 RAM cache)...");
        
        // Creating a new service simulates a server restart because the old 
        // in-memory Caffeine cache is destroyed and a fresh, empty one is created.
        ApiService newService = new ApiService();
        
        System.out.println("\n[Request 3 - After App Restart]");
        String result3 = newService.getData(apiUrl);
        System.out.println("Result: " + result3);
    }
}
