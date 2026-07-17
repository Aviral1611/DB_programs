package com.demo.apicache.service;

import com.demo.apicache.dao.ApiCacheDAO;
import com.demo.apicache.db.DatabaseConnection;
import com.demo.apicache.model.CacheEntry;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import java.sql.Connection;
import java.sql.SQLException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.TimeUnit;

public class ApiService {
    private ApiCacheDAO cacheDAO = new ApiCacheDAO();
    private static final long CACHE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes for Database expiration
    
    // L1 Cache (In-Memory RAM) using Caffeine
    private Cache<String, String> l1Cache = Caffeine.newBuilder()
            .expireAfterWrite(5, TimeUnit.MINUTES) // Auto-expires data in RAM after 5 minutes
            .maximumSize(1000) // Keep at most 1000 endpoints in RAM to save memory
            .build();

    public String getData(String endpoint) {
        // Step 1: Check L1 Cache (RAM)
        String ramData = l1Cache.getIfPresent(endpoint);
        if (ramData != null) {
            System.out.println(">>> [L1 CACHE HIT] Serving from Caffeine RAM Cache (0.1ms)");
            return ramData;
        }
        
        System.out.println(">>> [L1 CACHE MISS] Checking Database (L2)...");

        // Step 2: Check L2 Cache (Database)
        try (Connection conn = DatabaseConnection.getConnection()) {
            CacheEntry dbCache = cacheDAO.getCacheByEndpoint(conn, endpoint);
            long currentTime = System.currentTimeMillis();

            if (dbCache != null && (currentTime - dbCache.getTimestampMs()) < CACHE_EXPIRY_MS) {
                System.out.println(">>> [L2 CACHE HIT] Serving from MySQL Database (2-5ms)");
                // Promote back up to L1
                l1Cache.put(endpoint, dbCache.getResponse());
                return dbCache.getResponse();
            }

            System.out.println(">>> [L2 CACHE MISS / EXPIRED] Fetching from External API (L3)...");
            
            // Step 3: Fetch from L3 (Network API)
            String freshData = fetchFromNetwork(endpoint);
            
            // Save to L2 (Database)
            cacheDAO.saveOrUpdateCache(conn, endpoint, freshData, currentTime);
            
            // Save to L1 (RAM)
            l1Cache.put(endpoint, freshData);
            
            return freshData;

        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private String fetchFromNetwork(String targetUrl) throws Exception {
        URL url = new URL(targetUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        StringBuilder result = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                result.append(line);
            }
        }
        return result.toString();
    }
}
