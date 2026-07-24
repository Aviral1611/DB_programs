package com.demo.leaderboard.dao;

import com.demo.leaderboard.model.PlayerScore;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

public class LeaderboardDAO {

    /**
     * Registers a new player. Returns the generated player_id.
     * Uses UNIQUE constraint on username to prevent duplicates.
     */
    public int registerPlayer(Connection conn, String username) throws SQLException {
        String sql = "INSERT INTO players (username) VALUES (?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            pstmt.setString(1, username);
            pstmt.executeUpdate();
            try (ResultSet rs = pstmt.getGeneratedKeys()) {
                if (rs.next()) {
                    return rs.getInt(1);
                }
            }
        }
        throw new SQLException("Failed to register player: " + username);
    }

    /**
     * Submits a score for a player.
     * Every score is recorded — we never overwrite old scores.
     * This allows us to track improvement over time.
     */
    public void submitScore(Connection conn, int playerId, int score) throws SQLException {
        String sql = "INSERT INTO scores (player_id, score) VALUES (?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, playerId);
            pstmt.setInt(2, score);
            pstmt.executeUpdate();
        }
    }

    /**
     * Retrieves the leaderboard using MySQL Window Functions.
     *
     * This is the heart of the program. The query:
     * 1. Joins players with their scores
     * 2. Groups by player and finds their MAX score (personal best)
     * 3. Uses RANK() to assign rankings (with gaps for ties)
     * 4. Uses DENSE_RANK() to assign rankings (without gaps for ties)
     * 5. Counts total submissions per player
     * 6. Orders by best score descending
     */
    public List<PlayerScore> getLeaderboard(Connection conn, int limit) throws SQLException {
        List<PlayerScore> leaderboard = new ArrayList<>();

        String sql =
            "SELECT " +
            "   p.username, " +
            "   MAX(s.score) AS best_score, " +
            "   COUNT(s.score_id) AS total_submissions, " +
            "   RANK() OVER (ORDER BY MAX(s.score) DESC) AS player_rank, " +
            "   DENSE_RANK() OVER (ORDER BY MAX(s.score) DESC) AS player_dense_rank " +
            "FROM players p " +
            "JOIN scores s ON p.player_id = s.player_id " +
            "GROUP BY p.player_id, p.username " +
            "ORDER BY best_score DESC " +
            "LIMIT ?";

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, limit);
            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    PlayerScore ps = new PlayerScore();
                    ps.setUsername(rs.getString("username"));
                    ps.setBestScore(rs.getInt("best_score"));
                    ps.setTotalSubmissions(rs.getInt("total_submissions"));
                    ps.setRank(rs.getInt("player_rank"));
                    ps.setDenseRank(rs.getInt("player_dense_rank"));
                    leaderboard.add(ps);
                }
            }
        }
        return leaderboard;
    }

    /**
     * Retrieves a specific player's score history (all attempts).
     * Ordered newest to oldest so they can see their most recent score first.
     */
    public void displayPlayerHistory(Connection conn, String username) throws SQLException {
        String sql =
            "SELECT s.score, s.submitted_at, " +
            "   CASE WHEN s.score = (SELECT MAX(s2.score) FROM scores s2 WHERE s2.player_id = p.player_id) " +
            "       THEN '<-- PERSONAL BEST' ELSE '' END AS marker " +
            "FROM scores s " +
            "JOIN players p ON s.player_id = p.player_id " +
            "WHERE p.username = ? " +
            "ORDER BY s.submitted_at ASC";

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, username);
            try (ResultSet rs = pstmt.executeQuery()) {
                System.out.println("\n  --- Score History for '" + username + "' ---");
                int attempt = 1;
                while (rs.next()) {
                    System.out.printf("    Attempt %d: %5d pts at %s %s%n",
                        attempt++,
                        rs.getInt("score"),
                        rs.getTimestamp("submitted_at"),
                        rs.getString("marker"));
                }
            }
        }
    }

    /**
     * Cleans up tables for a fresh demo. Disables FK checks to allow TRUNCATE.
     */
    public void clearTables(Connection conn) throws SQLException {
        conn.createStatement().execute("SET FOREIGN_KEY_CHECKS = 0");
        conn.createStatement().execute("TRUNCATE TABLE scores");
        conn.createStatement().execute("TRUNCATE TABLE players");
        conn.createStatement().execute("SET FOREIGN_KEY_CHECKS = 1");
    }
}
