package com.demo.leaderboard.service;

import com.demo.leaderboard.dao.LeaderboardDAO;
import com.demo.leaderboard.db.DatabaseConnection;
import com.demo.leaderboard.model.PlayerScore;
import com.demo.leaderboard.util.ConfigLoader;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

/**
 * Business logic layer for the leaderboard system.
 * Coordinates player registration, score submissions, and ranking retrieval.
 */
public class LeaderboardService {
    private LeaderboardDAO leaderboardDAO = new LeaderboardDAO();
    private final int topLimit;

    public LeaderboardService() {
        this.topLimit = ConfigLoader.getInt("leaderboard.top.limit");
    }

    /**
     * Registers a player and returns their ID.
     */
    public int registerPlayer(String username) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            int playerId = leaderboardDAO.registerPlayer(conn, username);
            System.out.println("  [REGISTERED] " + username + " (ID: " + playerId + ")");
            return playerId;
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to register player '" + username + "': " + e.getMessage());
            e.printStackTrace();
            return -1;
        }
    }

    /**
     * Submits a score for a player.
     */
    public void submitScore(int playerId, String username, int score) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            leaderboardDAO.submitScore(conn, playerId, score);
            System.out.println("  [SCORE] " + username + " scored " + score + " pts");
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to submit score: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Displays the live leaderboard with RANK and DENSE_RANK.
     */
    public void displayLeaderboard() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            List<PlayerScore> leaderboard = leaderboardDAO.getLeaderboard(conn, topLimit);
            System.out.println("\n===== LIVE LEADERBOARD (Top " + topLimit + ") =====");
            System.out.println("  Rank (Dense)      | Player          | Best Score     | Attempts");
            System.out.println("  " + "-".repeat(70));
            if (leaderboard.isEmpty()) {
                System.out.println("  No scores submitted yet.");
            } else {
                for (PlayerScore ps : leaderboard) {
                    System.out.println(ps.toString());
                }
            }
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to retrieve leaderboard: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Shows a specific player's full score history with personal best marker.
     */
    public void showPlayerHistory(String username) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            leaderboardDAO.displayPlayerHistory(conn, username);
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to retrieve player history: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Clears all data for a fresh demo.
     */
    public void clearData() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            leaderboardDAO.clearTables(conn);
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to clear data: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
