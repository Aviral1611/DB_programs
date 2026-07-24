import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    "Program13_Leaderboard/leaderboard_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_leaderboard;
USE demo_leaderboard;

CREATE TABLE IF NOT EXISTS players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    score INT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    INDEX idx_player_score (player_id, score DESC)
);
""",

    "Program13_Leaderboard/config.properties": """# ============================================
# Program 13 - Leaderboard Configuration
# ============================================

# Database Configuration
db.url=jdbc:mysql://localhost:3306/demo_leaderboard
db.user=root
db.password=root

# Leaderboard Settings
leaderboard.top.limit=10
""",

    "Program13_Leaderboard/src/com/demo/leaderboard/util/ConfigLoader.java": """package com.demo.leaderboard.util;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Loads configuration from an external properties file.
 * Eliminates hardcoded values — ops teams can change settings
 * without recompiling the Java code.
 */
public class ConfigLoader {
    private static final Properties properties = new Properties();
    private static boolean loaded = false;

    public static synchronized void load() {
        if (loaded) return;

        try (InputStream input = new FileInputStream("config.properties")) {
            properties.load(input);
            loaded = true;
            System.out.println("[CONFIG] Loaded config.properties successfully.");
        } catch (IOException e) {
            System.err.println("[CONFIG ERROR] Failed to load config.properties: " + e.getMessage());
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

    "Program13_Leaderboard/src/com/demo/leaderboard/db/DatabaseConnection.java": """package com.demo.leaderboard.db;

import com.demo.leaderboard.util.ConfigLoader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Database connection factory.
 * Reads credentials from config.properties — zero hardcoding.
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

    "Program13_Leaderboard/src/com/demo/leaderboard/model/PlayerScore.java": """package com.demo.leaderboard.model;

/**
 * Represents a player's ranking entry on the leaderboard.
 * Contains both their best score and their computed rank.
 */
public class PlayerScore {
    private String username;
    private int bestScore;
    private int rank;
    private int denseRank;
    private int totalSubmissions;

    public PlayerScore() {}

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public int getBestScore() { return bestScore; }
    public void setBestScore(int bestScore) { this.bestScore = bestScore; }

    public int getRank() { return rank; }
    public void setRank(int rank) { this.rank = rank; }

    public int getDenseRank() { return denseRank; }
    public void setDenseRank(int denseRank) { this.denseRank = denseRank; }

    public int getTotalSubmissions() { return totalSubmissions; }
    public void setTotalSubmissions(int totalSubmissions) { this.totalSubmissions = totalSubmissions; }

    @Override
    public String toString() {
        return String.format("  #%-3d (Dense: #%-3d) | %-15s | Best: %5d pts | Attempts: %d",
            rank, denseRank, username, bestScore, totalSubmissions);
    }
}
""",

    "Program13_Leaderboard/src/com/demo/leaderboard/dao/LeaderboardDAO.java": """package com.demo.leaderboard.dao;

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
                System.out.println("\\n  --- Score History for '" + username + "' ---");
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
""",

    "Program13_Leaderboard/src/com/demo/leaderboard/service/LeaderboardService.java": """package com.demo.leaderboard.service;

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
            System.out.println("\\n===== LIVE LEADERBOARD (Top " + topLimit + ") =====");
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
""",

    "Program13_Leaderboard/src/com/demo/leaderboard/main/LeaderboardMain.java": """package com.demo.leaderboard.main;

import com.demo.leaderboard.service.LeaderboardService;
import com.demo.leaderboard.util.ConfigLoader;

public class LeaderboardMain {
    public static void main(String[] args) {
        System.out.println("=== Gaming Leaderboard (Window Functions) ===\\n");

        ConfigLoader.load();
        LeaderboardService service = new LeaderboardService();
        service.clearData();

        // 1. Register players
        System.out.println("[Step 1] Registering players...");
        int p1 = service.registerPlayer("ShadowNinja");
        int p2 = service.registerPlayer("DragonSlayer");
        int p3 = service.registerPlayer("PixelQueen");
        int p4 = service.registerPlayer("CodeWizard");
        int p5 = service.registerPlayer("StormBreaker");

        // 2. Submit multiple scores per player (simulating multiple game rounds)
        System.out.println("\\n[Step 2] Playing rounds and submitting scores...");

        // ShadowNinja plays 3 rounds, improving each time
        service.submitScore(p1, "ShadowNinja", 720);
        service.submitScore(p1, "ShadowNinja", 850);
        service.submitScore(p1, "ShadowNinja", 940);

        // DragonSlayer plays 2 rounds
        service.submitScore(p2, "DragonSlayer", 880);
        service.submitScore(p2, "DragonSlayer", 760);

        // PixelQueen plays 4 rounds — scores a tie with ShadowNinja's best!
        service.submitScore(p3, "PixelQueen", 600);
        service.submitScore(p3, "PixelQueen", 710);
        service.submitScore(p3, "PixelQueen", 940);  // TIE with ShadowNinja!
        service.submitScore(p3, "PixelQueen", 800);

        // CodeWizard plays 1 round
        service.submitScore(p4, "CodeWizard", 990);

        // StormBreaker plays 2 rounds
        service.submitScore(p5, "StormBreaker", 850);
        service.submitScore(p5, "StormBreaker", 830);

        // 3. Display the live leaderboard
        service.displayLeaderboard();

        // 4. Show individual player history
        System.out.println("\\n[Step 4] Player Deep Dive...");
        service.showPlayerHistory("ShadowNinja");
        service.showPlayerHistory("PixelQueen");
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Program 13 generated successfully!")
