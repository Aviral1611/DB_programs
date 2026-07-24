package com.demo.audit.service;

import com.demo.audit.dao.DocumentDAO;
import com.demo.audit.db.DatabaseConnection;
import com.demo.audit.util.ConfigLoader;
import java.sql.Connection;
import java.sql.SQLException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class AuditService {
    private DocumentDAO docDAO = new DocumentDAO();

    public void runAuditDemo() {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            
            // Clean slate for demo (Disable FK checks temporarily to truncate)
            conn.createStatement().execute("SET FOREIGN_KEY_CHECKS = 0");
            conn.createStatement().execute("TRUNCATE TABLE document_history");
            conn.createStatement().execute("TRUNCATE TABLE documents");
            conn.createStatement().execute("SET FOREIGN_KEY_CHECKS = 1");
            
            // We use transactions because we want the history update and document update to be atomic
            conn.setAutoCommit(false);
            
            System.out.println("1. Alice creates the initial document (v1)...");
            String docId = generateUuidFromApi();
            if (docId == null) {
                System.out.println("Failed to get UUID from API. Aborting.");
                return;
            }
            System.out.println("   [API] Generated UUID: " + docId);
            docDAO.createDocument(conn, docId, "Project Alpha - Draft", "This is the initial draft.", "Alice");
            conn.commit(); // Commit the creation
            
            // Sleep so timestamps look distinct
            Thread.sleep(1000); 

            System.out.println("\n2. Bob edits the document...");
            docDAO.updateDocument(conn, docId, "Project Alpha - V2", "Added budget section to the draft.", "Bob");
            conn.commit();

            Thread.sleep(1000);

            System.out.println("\n3. Charlie makes the final edits...");
            docDAO.updateDocument(conn, docId, "Project Alpha - Final", "Budget approved. Ready for launch.", "Charlie");
            conn.commit();

            // Display the audit trail with version numbers
            docDAO.displayHistory(conn, docId);

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

    /**
     * Fetches a UUID from an external API.
     * The API URL is read from config.properties — not hardcoded.
     */
    private String generateUuidFromApi() {
        try {
            String apiUrl = ConfigLoader.get("uuid.api.url");
            URL url = new URL(apiUrl);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
                return reader.readLine(); // The API returns a single line with the UUID
            }
        } catch (Exception e) {
            System.err.println("[API ERROR] Failed to generate UUID: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
}
