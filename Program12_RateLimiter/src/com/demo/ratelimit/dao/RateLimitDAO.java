package com.demo.ratelimit.dao;

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
