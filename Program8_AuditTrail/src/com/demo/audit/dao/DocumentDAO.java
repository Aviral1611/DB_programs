package com.demo.audit.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class DocumentDAO {

    public int createDocument(Connection conn, String title, String content, String author) throws SQLException {
        String sql = "INSERT INTO documents (title, content, last_updated_by) VALUES (?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            pstmt.setString(1, title);
            pstmt.setString(2, content);
            pstmt.setString(3, author);
            pstmt.executeUpdate();
            
            try (ResultSet rs = pstmt.getGeneratedKeys()) {
                if (rs.next()) {
                    return rs.getInt(1);
                }
            }
        }
        return -1;
    }

    public void updateDocument(Connection conn, int docId, String newTitle, String newContent, String editor) throws SQLException {
        // Step 1: Fetch the current version of the document and lock the row using FOR UPDATE
        String selectSql = "SELECT title, content FROM documents WHERE doc_id = ? FOR UPDATE";
        String insertHistorySql = "INSERT INTO document_history (doc_id, old_title, old_content, changed_by) VALUES (?, ?, ?, ?)";
        String updateDocSql = "UPDATE documents SET title = ?, content = ?, last_updated_by = ? WHERE doc_id = ?";

        String oldTitle = null;
        String oldContent = null;

        try (PreparedStatement selectStmt = conn.prepareStatement(selectSql)) {
            selectStmt.setInt(1, docId);
            try (ResultSet rs = selectStmt.executeQuery()) {
                if (rs.next()) {
                    oldTitle = rs.getString("title");
                    oldContent = rs.getString("content");
                } else {
                    throw new SQLException("Document not found!");
                }
            }
        }

        // Step 2: Save the old version to the history table
        try (PreparedStatement historyStmt = conn.prepareStatement(insertHistorySql)) {
            historyStmt.setInt(1, docId);
            historyStmt.setString(2, oldTitle);
            historyStmt.setString(3, oldContent);
            historyStmt.setString(4, editor); // The person making the change
            historyStmt.executeUpdate();
        }

        // Step 3: Update the actual document
        try (PreparedStatement updateStmt = conn.prepareStatement(updateDocSql)) {
            updateStmt.setString(1, newTitle);
            updateStmt.setString(2, newContent);
            updateStmt.setString(3, editor);
            updateStmt.setInt(4, docId);
            updateStmt.executeUpdate();
        }
    }

    public void displayHistory(Connection conn, int docId) throws SQLException {
        // Display current document
        String currentSql = "SELECT * FROM documents WHERE doc_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(currentSql)) {
            pstmt.setInt(1, docId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    System.out.println("\n--- Current Version (Live) ---");
                    System.out.println("Title: " + rs.getString("title"));
                    System.out.println("Content: " + rs.getString("content"));
                    System.out.println("Last Updated By: " + rs.getString("last_updated_by") + " at " + rs.getTimestamp("last_updated_at"));
                }
            }
        }

        // Display history trail
        String historySql = "SELECT * FROM document_history WHERE doc_id = ? ORDER BY changed_at DESC";
        try (PreparedStatement pstmt = conn.prepareStatement(historySql)) {
            pstmt.setInt(1, docId);
            try (ResultSet rs = pstmt.executeQuery()) {
                System.out.println("\n--- Version History Trail (Newest to Oldest) ---");
                while (rs.next()) {
                    System.out.println("Previous Version saved by: " + rs.getString("changed_by") + " on " + rs.getTimestamp("changed_at"));
                    System.out.println("  Old Title: " + rs.getString("old_title"));
                    System.out.println("  Old Content: " + rs.getString("old_content"));
                    System.out.println("  -------------------------");
                }
            }
        }
    }
}
