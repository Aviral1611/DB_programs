package com.demo.apicache.main;

import com.demo.apicache.service.ApiService;

public class ApiCacheMain {
    public static void main(String[] args) {
        System.out.println("=== API Caching System (L1 + L2 Architecture) ===");
        ApiService service = new ApiService();
        String apiUrl = "https://api.agify.io?name=java";

        System.out.println("\n[Request 1 - Cold Start]");
        String result1 = service.getData(apiUrl);

        System.out.println("\n[Request 2 - Immediate follow-up]");
        String result2 = service.getData(apiUrl);
        
        System.out.println("\nNote: To see an L2 Database hit, you would typically restart this application.");
        System.out.println("Because the RAM cache (L1) is destroyed on exit, but the Database (L2) persists,");
        System.out.println("the next time you run this, Request 1 will be an [L2 CACHE HIT]!");
    }
}
