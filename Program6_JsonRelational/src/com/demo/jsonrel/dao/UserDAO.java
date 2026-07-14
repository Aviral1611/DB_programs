package com.demo.jsonrel.dao;

import com.demo.jsonrel.model.User;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class UserDAO {
    public void insertUserWithHobbies(Connection conn, User user) throws SQLException {
        String insertUserSql = "INSERT INTO users (user_id, name) VALUES (?, ?) ON DUPLICATE KEY UPDATE name = VALUES(name)";
        String insertHobbySql = "INSERT INTO user_hobbies (user_id, hobby) VALUES (?, ?)";

        try (PreparedStatement userStmt = conn.prepareStatement(insertUserSql)) {
            userStmt.setInt(1, user.getId());
            userStmt.setString(2, user.getName());
            userStmt.executeUpdate();
        }

        try (PreparedStatement hobbyStmt = conn.prepareStatement(insertHobbySql)) {
            for (String hobby : user.getHobbies()) {
                hobbyStmt.setInt(1, user.getId());
                hobbyStmt.setString(2, hobby);
                hobbyStmt.executeUpdate();
            }
        }
    }

    public void displayAllUsersAndHobbies(Connection conn) throws SQLException {
        String sql = "SELECT u.name, h.hobby FROM users u JOIN user_hobbies h ON u.user_id = h.user_id ORDER BY u.name";
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            
            String currentUser = "";
            while (rs.next()) {
                String name = rs.getString("name");
                String hobby = rs.getString("hobby");

                if (!name.equals(currentUser)) {
                    System.out.println("\nUser: " + name);
                    currentUser = name;
                }
                System.out.println("  - Hobby: " + hobby);
            }
        }
    }

    public void clearTables(Connection conn) throws SQLException {
        conn.createStatement().execute("DELETE FROM user_hobbies");
        conn.createStatement().execute("DELETE FROM users");
    }
}
