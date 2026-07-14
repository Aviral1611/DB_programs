package com.demo.apicache.main;

import com.demo.apicache.service.ApiService;

public class ApiCacheMain {
    public static void main(String[] args) {
        System.out.println("=== API Caching System ===");
        ApiService service = new ApiService();
        String apiUrl = "https://api.agify.io?name=java";

        System.out.println("\n[Request 1]");
        String result1 = service.getData(apiUrl);
        System.out.println("Result: " + result1);

        System.out.println("\n[Request 2 - Immediate follow-up]");
        String result2 = service.getData(apiUrl);
        System.out.println("Result: " + result2);
    }
}
