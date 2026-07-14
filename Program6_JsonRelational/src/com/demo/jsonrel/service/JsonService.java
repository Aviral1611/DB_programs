package com.demo.jsonrel.service;

import com.demo.jsonrel.dao.UserDAO;
import com.demo.jsonrel.db.DatabaseConnection;
import com.demo.jsonrel.model.User;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

public class JsonService {
    private UserDAO userDAO = new UserDAO();
    private ObjectMapper mapper = new ObjectMapper();

    public void processJsonToDatabase(String jsonPayload) {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            conn.setAutoCommit(false);
            
            userDAO.clearTables(conn);

            // Using Jackson for robust JSON parsing
            List<User> users = mapper.readValue(jsonPayload, new TypeReference<List<User>>() {});

            for (User user : users) {
                userDAO.insertUserWithHobbies(conn, user);
            }

            conn.commit();
            System.out.println("Successfully parsed JSON using Jackson and inserted into relational tables.");
        } catch (Exception e) {
            if (conn != null) {
                try { conn.rollback(); } catch (SQLException ex) { ex.printStackTrace(); }
            }
            e.printStackTrace();
        } finally {
            if (conn != null) {
                try {
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }
    }

    public void showNormalizedData() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            System.out.println("\n[Current Relational Data from DB]");
            userDAO.displayAllUsersAndHobbies(conn);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
