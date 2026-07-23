package com.demo.urlshort.dao;

import com.demo.urlshort.model.ShortUrl;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class UrlDAO {

    /**
     * Inserts a new short URL mapping into the database.
     * Uses a unique constraint on short_code to prevent collisions.
     */
    public void insertShortUrl(Connection conn, String shortCode, String originalUrl) throws SQLException {
        String sql = "INSERT INTO short_urls (short_code, original_url) VALUES (?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, shortCode);
            pstmt.setString(2, originalUrl);
            pstmt.executeUpdate();
        }
    }

    /**
     * Checks if a short code already exists in the database.
     * This is used for collision detection during code generation.
     */
    public boolean shortCodeExists(Connection conn, String shortCode) throws SQLException {
        String sql = "SELECT 1 FROM short_urls WHERE short_code = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, shortCode);
            try (ResultSet rs = pstmt.executeQuery()) {
                return rs.next();
            }
        }
    }

    /**
     * Simulates a "click" on the short URL.
     * Atomically increments the click counter and returns the original URL.
     * Uses a transaction to ensure the increment and read are consistent.
     */
    public String resolveAndTrackClick(Connection conn, String shortCode) throws SQLException {
        String originalUrl = null;

        // Step 1: Atomically increment the click count
        String updateSql = "UPDATE short_urls SET click_count = click_count + 1 WHERE short_code = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(updateSql)) {
            pstmt.setString(1, shortCode);
            int rowsAffected = pstmt.executeUpdate();
            if (rowsAffected == 0) {
                throw new SQLException("Short code '" + shortCode + "' not found in database.");
            }
        }

        // Step 2: Fetch the original URL
        String selectSql = "SELECT original_url FROM short_urls WHERE short_code = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(selectSql)) {
            pstmt.setString(1, shortCode);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    originalUrl = rs.getString("original_url");
                }
            }
        }

        return originalUrl;
    }

    /**
     * Retrieves all short URLs with their analytics, sorted by most clicked.
     */
    public List<ShortUrl> getAllUrlsSortedByClicks(Connection conn) throws SQLException {
        List<ShortUrl> urls = new ArrayList<>();
        String sql = "SELECT * FROM short_urls ORDER BY click_count DESC";
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                ShortUrl url = new ShortUrl();
                url.setId(rs.getInt("id"));
                url.setShortCode(rs.getString("short_code"));
                url.setOriginalUrl(rs.getString("original_url"));
                url.setClickCount(rs.getInt("click_count"));
                url.setCreatedAt(rs.getTimestamp("created_at"));
                urls.add(url);
            }
        }
        return urls;
    }

    public void clearTable(Connection conn) throws SQLException {
        try (PreparedStatement pstmt = conn.prepareStatement("TRUNCATE TABLE short_urls")) {
            pstmt.executeUpdate();
        }
    }
}
