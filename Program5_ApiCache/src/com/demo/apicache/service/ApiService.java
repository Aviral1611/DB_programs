package com.demo.apicache.service;

import com.demo.apicache.dao.ApiCacheDAO;
import com.demo.apicache.db.DatabaseConnection;
import com.demo.apicache.model.CacheEntry;
import java.sql.Connection;
import java.sql.SQLException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class ApiService {
    private ApiCacheDAO cacheDAO = new ApiCacheDAO();
    private static final long CACHE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes

    public String getData(String endpoint) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            CacheEntry cache = cacheDAO.getCacheByEndpoint(conn, endpoint);
            long currentTime = System.currentTimeMillis();

            if (cache != null && (currentTime - cache.getTimestampMs()) < CACHE_EXPIRY_MS) {
                System.out.println(">>> Serving from Database Cache (No network call)");
                return cache.getResponse();
            }

            System.out.println(">>> Cache miss or expired. Fetching from Network...");
            String freshData = fetchFromNetwork(endpoint);
            
            cacheDAO.saveOrUpdateCache(conn, endpoint, freshData, currentTime);
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
