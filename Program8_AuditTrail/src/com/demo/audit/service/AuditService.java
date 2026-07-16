package com.demo.audit.service;

import com.demo.audit.dao.DocumentDAO;
import com.demo.audit.db.DatabaseConnection;
import java.sql.Connection;
import java.sql.SQLException;

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
            
            System.out.println("1. Alice creates the initial document...");
            int docId = docDAO.createDocument(conn, "Project Alpha - Draft", "This is the initial draft.", "Alice");
            conn.commit(); // Commit the creation
            
            // Sleep so timestamps look distinct
            Thread.sleep(1000); 

            System.out.println("2. Bob edits the document...");
            docDAO.updateDocument(conn, docId, "Project Alpha - V2", "Added budget section to the draft.", "Bob");
            conn.commit();

            Thread.sleep(1000);

            System.out.println("3. Charlie makes the final edits...");
            docDAO.updateDocument(conn, docId, "Project Alpha - Final", "Budget approved. Ready for launch.", "Charlie");
            conn.commit();

            // Display the audit trail
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
}
