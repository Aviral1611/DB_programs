package com.demo.urlshort.service;

import com.demo.urlshort.dao.UrlDAO;
import com.demo.urlshort.db.DatabaseConnection;
import com.demo.urlshort.model.ShortUrl;
import java.sql.Connection;
import java.sql.SQLException;
import java.security.SecureRandom;
import java.util.List;

public class UrlService {
    private UrlDAO urlDAO = new UrlDAO();

    // Base62 character set: [0-9, a-z, A-Z] = 62 characters
    private static final String BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private static final int CODE_LENGTH = 6;
    private static final int MAX_COLLISION_RETRIES = 5;
    private SecureRandom random = new SecureRandom();

    /**
     * Generates a cryptographically random Base62 short code.
     * Uses SecureRandom instead of Random for unpredictability.
     */
    private String generateShortCode() {
        StringBuilder code = new StringBuilder(CODE_LENGTH);
        for (int i = 0; i < CODE_LENGTH; i++) {
            int index = random.nextInt(BASE62_CHARS.length());
            code.append(BASE62_CHARS.charAt(index));
        }
        return code.toString();
    }

    /**
     * Shortens a URL with collision detection.
     * If the generated code already exists in the DB, it retries up to MAX_COLLISION_RETRIES times.
     */
    public String shortenUrl(String originalUrl) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            String shortCode = null;
            boolean inserted = false;

            for (int attempt = 1; attempt <= MAX_COLLISION_RETRIES; attempt++) {
                shortCode = generateShortCode();
                
                if (!urlDAO.shortCodeExists(conn, shortCode)) {
                    urlDAO.insertShortUrl(conn, shortCode, originalUrl);
                    inserted = true;
                    break;
                } else {
                    System.out.println("   [COLLISION] Code '" + shortCode + "' already exists. Retrying... (Attempt " + attempt + ")");
                }
            }

            if (!inserted) {
                throw new RuntimeException("Failed to generate a unique short code after " + MAX_COLLISION_RETRIES + " attempts.");
            }

            return shortCode;

        } catch (SQLException e) {
            System.err.println("[ERROR] Database error while shortening URL: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Resolves a short code back to the original URL and tracks the click.
     */
    public String resolveUrl(String shortCode) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            return urlDAO.resolveAndTrackClick(conn, shortCode);
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to resolve short code '" + shortCode + "': " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Displays click analytics for all shortened URLs.
     */
    public void displayAnalytics() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            List<ShortUrl> urls = urlDAO.getAllUrlsSortedByClicks(conn);
            System.out.println("\n--- Click Analytics (Sorted by Most Clicked) ---");
            if (urls.isEmpty()) {
                System.out.println("No URLs found.");
            } else {
                for (ShortUrl url : urls) {
                    System.out.println("  " + url.toString());
                }
            }
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to retrieve analytics: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Clears all data for a fresh demo run.
     */
    public void clearData() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            urlDAO.clearTable(conn);
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to clear table: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
