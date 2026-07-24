import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    "Program12_RateLimiter/ratelimit_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_ratelimiter;
USE demo_ratelimiter;

CREATE TABLE IF NOT EXISTS rate_limit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    requested_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_user_endpoint_time (user_id, endpoint, requested_at)
);
""",

    "Program12_RateLimiter/config.properties": """# ============================================
# Program 12 - Rate Limiter Configuration
# ============================================

# Database Configuration
db.url=jdbc:mysql://localhost:3306/demo_ratelimiter
db.user=root
db.password=root

# Rate Limiting Rules
ratelimit.max.requests=5
ratelimit.window.seconds=60

# Cleanup Policy
ratelimit.cleanup.older.than.minutes=10
""",

    "Program12_RateLimiter/src/com/demo/ratelimit/util/ConfigLoader.java": """package com.demo.ratelimit.util;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Loads configuration from an external properties file.
 * This eliminates hardcoded values and allows ops teams to change
 * settings without recompiling the Java code.
 */
public class ConfigLoader {
    private static final Properties properties = new Properties();
    private static boolean loaded = false;

    /**
     * Loads the config.properties file from the project root.
     * Uses synchronized block to ensure thread-safe loading.
     */
    public static synchronized void load() {
        if (loaded) return;

        try (InputStream input = new FileInputStream("config.properties")) {
            properties.load(input);
            loaded = true;
            System.out.println("[CONFIG] Loaded config.properties successfully.");
        } catch (IOException e) {
            System.err.println("[CONFIG ERROR] Failed to load config.properties: " + e.getMessage());
            System.err.println("[CONFIG ERROR] Make sure config.properties is in the project root directory.");
            throw new RuntimeException("Cannot start application without configuration.", e);
        }
    }

    public static String get(String key) {
        if (!loaded) load();
        String value = properties.getProperty(key);
        if (value == null) {
            throw new RuntimeException("[CONFIG ERROR] Missing required property: " + key);
        }
        return value.trim();
    }

    public static int getInt(String key) {
        return Integer.parseInt(get(key));
    }
}
""",

    "Program12_RateLimiter/src/com/demo/ratelimit/db/DatabaseConnection.java": """package com.demo.ratelimit.db;

import com.demo.ratelimit.util.ConfigLoader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Database connection factory.
 * Reads credentials from config.properties instead of hardcoding them.
 */
public class DatabaseConnection {

    public static Connection getConnection() throws SQLException {
        String url = ConfigLoader.get("db.url");
        String user = ConfigLoader.get("db.user");
        String password = ConfigLoader.get("db.password");
        return DriverManager.getConnection(url, user, password);
    }
}
""",

    "Program12_RateLimiter/src/com/demo/ratelimit/model/RateLimitResult.java": """package com.demo.ratelimit.model;

/**
 * Immutable result object returned after a rate limit check.
 * Contains whether the request is allowed and diagnostic metadata.
 */
public class RateLimitResult {
    private final boolean allowed;
    private final int currentCount;
    private final int maxAllowed;
    private final int windowSeconds;

    public RateLimitResult(boolean allowed, int currentCount, int maxAllowed, int windowSeconds) {
        this.allowed = allowed;
        this.currentCount = currentCount;
        this.maxAllowed = maxAllowed;
        this.windowSeconds = windowSeconds;
    }

    public boolean isAllowed() { return allowed; }
    public int getCurrentCount() { return currentCount; }
    public int getMaxAllowed() { return maxAllowed; }
    public int getWindowSeconds() { return windowSeconds; }

    @Override
    public String toString() {
        if (allowed) {
            return String.format("[200 OK] Request ALLOWED (%d/%d used in last %ds)", currentCount, maxAllowed, windowSeconds);
        } else {
            return String.format("[429 TOO MANY REQUESTS] BLOCKED! (%d/%d used in last %ds)", currentCount, maxAllowed, windowSeconds);
        }
    }
}
""",

    "Program12_RateLimiter/src/com/demo/ratelimit/dao/RateLimitDAO.java": """package com.demo.ratelimit.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;

public class RateLimitDAO {

    /**
     * Logs a request into the rate_limit_log table.
     * Every single API call gets recorded here for auditing and counting.
     */
    public void logRequest(Connection conn, String userId, String endpoint) throws SQLException {
        String sql = "INSERT INTO rate_limit_log (user_id, endpoint) VALUES (?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, userId);
            pstmt.setString(2, endpoint);
            pstmt.executeUpdate();
        }
    }

    /**
     * Counts how many requests a specific user has made to a specific endpoint
     * within the given time window (sliding window algorithm).
     *
     * The SQL query:
     *   SELECT COUNT(*) FROM rate_limit_log
     *   WHERE user_id = ? AND endpoint = ?
     *   AND requested_at >= NOW() - INTERVAL ? SECOND
     *
     * This is a "sliding window" because the window moves forward in real-time.
     * A request made 61 seconds ago automatically falls outside a 60-second window.
     */
    public int countRequestsInWindow(Connection conn, String userId, String endpoint, int windowSeconds) throws SQLException {
        String sql = "SELECT COUNT(*) AS request_count FROM rate_limit_log " +
                     "WHERE user_id = ? AND endpoint = ? " +
                     "AND requested_at >= NOW(3) - INTERVAL ? SECOND";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, userId);
            pstmt.setString(2, endpoint);
            pstmt.setInt(3, windowSeconds);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt("request_count");
                }
            }
        }
        return 0;
    }

    /**
     * Cleans up old log entries that are older than the specified number of minutes.
     * This prevents the table from growing infinitely and keeps queries fast.
     * In production, this would typically run as a scheduled cron job.
     */
    public int cleanupOldEntries(Connection conn, int olderThanMinutes) throws SQLException {
        String sql = "DELETE FROM rate_limit_log WHERE requested_at < NOW() - INTERVAL ? MINUTE";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, olderThanMinutes);
            return pstmt.executeUpdate();
        }
    }

    /**
     * Truncates the table for a fresh demo run.
     */
    public void clearTable(Connection conn) throws SQLException {
        try (PreparedStatement pstmt = conn.prepareStatement("TRUNCATE TABLE rate_limit_log")) {
            pstmt.executeUpdate();
        }
    }
}
""",

    "Program12_RateLimiter/src/com/demo/ratelimit/service/RateLimitService.java": """package com.demo.ratelimit.service;

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
""",

    "Program12_RateLimiter/src/com/demo/ratelimit/main/RateLimitMain.java": """package com.demo.ratelimit.main;

import com.demo.ratelimit.model.RateLimitResult;
import com.demo.ratelimit.service.RateLimitService;
import com.demo.ratelimit.util.ConfigLoader;

public class RateLimitMain {
    public static void main(String[] args) {
        System.out.println("=== API Rate Limiter (Sliding Window) ===\\n");

        // Load configuration from config.properties
        ConfigLoader.load();

        RateLimitService service = new RateLimitService();
        service.clearData();

        String userId = "user_aviral";
        String endpoint = "/api/v1/data";

        // Simulate 8 rapid API calls from the same user
        System.out.println("\\n[Scenario 1] User '" + userId + "' makes 8 rapid requests to '" + endpoint + "':");
        System.out.println("(Limit is 5 requests per 60 seconds)\\n");

        for (int i = 1; i <= 8; i++) {
            RateLimitResult result = service.checkAndLog(userId, endpoint);
            System.out.println("  Request #" + i + ": " + result);
        }

        // A different user should NOT be affected by user_aviral's rate limit
        System.out.println("\\n[Scenario 2] A different user makes a request to the same endpoint:");
        String otherUser = "user_bob";
        RateLimitResult bobResult = service.checkAndLog(otherUser, endpoint);
        System.out.println("  " + otherUser + ": " + bobResult);

        // Same user, different endpoint should also work independently
        System.out.println("\\n[Scenario 3] Same user '" + userId + "' hits a DIFFERENT endpoint:");
        String otherEndpoint = "/api/v1/reports";
        RateLimitResult otherEndpointResult = service.checkAndLog(userId, otherEndpoint);
        System.out.println("  " + otherEndpoint + ": " + otherEndpointResult);

        // Cleanup
        System.out.println("\\n[Housekeeping] Running cleanup job...");
        service.cleanup();
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Program 12 generated successfully!")
