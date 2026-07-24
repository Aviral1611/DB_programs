package com.demo.ratelimit.service;

import com.demo.ratelimit.dao.RateLimitDAO;
import com.demo.ratelimit.db.DatabaseConnection;
import com.demo.ratelimit.model.RateLimitResult;
import com.demo.ratelimit.util.ConfigLoader;
import java.sql.Connection;
import java.sql.SQLException;

/**
 * Core rate limiting engine.
 * Reads thresholds from config.properties and enforces them per user per endpoint.
 */
public class RateLimitService {
    private RateLimitDAO rateLimitDAO = new RateLimitDAO();
    private final int maxRequests;
    private final int windowSeconds;
    private final int cleanupMinutes;

    public RateLimitService() {
        this.maxRequests = ConfigLoader.getInt("ratelimit.max.requests");
        this.windowSeconds = ConfigLoader.getInt("ratelimit.window.seconds");
        this.cleanupMinutes = ConfigLoader.getInt("ratelimit.cleanup.older.than.minutes");
        System.out.println("[CONFIG] Rate Limit: " + maxRequests + " requests per " + windowSeconds + " seconds");
    }

    /**
     * The main rate-limiting method. Called before every API request.
     *
     * Flow:
     * 1. Count existing requests in the current sliding window.
     * 2. If count >= max, REJECT the request (return 429).
     * 3. If count < max, LOG the request and ALLOW it (return 200).
     */
    public RateLimitResult checkAndLog(String userId, String endpoint) {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            conn.setAutoCommit(false); // Transaction: count + insert must be atomic

            // Step 1: Count requests in the sliding window
            int currentCount = rateLimitDAO.countRequestsInWindow(conn, userId, endpoint, windowSeconds);

            // Step 2: Decide
            if (currentCount >= maxRequests) {
                conn.rollback(); // No changes needed, just release the transaction
                return new RateLimitResult(false, currentCount, maxRequests, windowSeconds);
            }

            // Step 3: Log the request and allow it
            rateLimitDAO.logRequest(conn, userId, endpoint);
            conn.commit();

            return new RateLimitResult(true, currentCount + 1, maxRequests, windowSeconds);

        } catch (SQLException e) {
            if (conn != null) {
                try { conn.rollback(); } catch (SQLException ex) { ex.printStackTrace(); }
            }
            System.err.println("[DB ERROR] Rate limit check failed: " + e.getMessage());
            e.printStackTrace();
            // Fail-open: if the database is down, allow the request rather than blocking users
            return new RateLimitResult(true, 0, maxRequests, windowSeconds);

        } finally {
            if (conn != null) {
                try {
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException e) { e.printStackTrace(); }
            }
        }
    }

    /**
     * Housekeeping: removes stale log entries to keep the table lean.
     */
    public void cleanup() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            int deleted = rateLimitDAO.cleanupOldEntries(conn, cleanupMinutes);
            System.out.println("[CLEANUP] Removed " + deleted + " stale log entries older than " + cleanupMinutes + " minutes.");
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Cleanup failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Clears all data for a fresh demo.
     */
    public void clearData() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            rateLimitDAO.clearTable(conn);
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to clear data: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
