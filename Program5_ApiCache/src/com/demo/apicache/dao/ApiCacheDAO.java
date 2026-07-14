package com.demo.apicache.dao;

import com.demo.apicache.model.CacheEntry;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class ApiCacheDAO {
    public CacheEntry getCacheByEndpoint(Connection conn, String endpoint) throws SQLException {
        String sql = "SELECT * FROM api_cache WHERE endpoint = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, endpoint);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return new CacheEntry(
                        rs.getString("endpoint"),
                        rs.getString("response"),
                        rs.getLong("timestamp_ms")
                    );
                }
            }
        }
        return null;
    }

    public void saveOrUpdateCache(Connection conn, String endpoint, String response, long timestampMs) throws SQLException {
        String sql = "INSERT INTO api_cache (endpoint, response, timestamp_ms) VALUES (?, ?, ?) " +
                     "ON DUPLICATE KEY UPDATE response = VALUES(response), timestamp_ms = VALUES(timestamp_ms)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, endpoint);
            pstmt.setString(2, response);
            pstmt.setLong(3, timestampMs);
            pstmt.executeUpdate();
        }
    }
}
