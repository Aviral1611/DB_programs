package com.demo.audit.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class DocumentDAO {

    public void createDocument(Connection conn, String docId, String title, String content, String author) throws SQLException {
        String sql = "INSERT INTO documents (doc_id, title, content, last_updated_by) VALUES (?, ?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, docId);
            pstmt.setString(2, title);
            pstmt.setString(3, content);
            pstmt.setString(4, author);
            pstmt.executeUpdate();
        }
    }

    /**
     * Gets the next version number for a document by counting existing history entries.
     * Version 1 = the first edit (archiving the original draft).
     */
    private int getNextVersionNumber(Connection conn, String docId) throws SQLException {
        String sql = "SELECT COALESCE(MAX(version_number), 0) + 1 AS next_version FROM document_history WHERE doc_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, docId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return rs.getInt("next_version");
                }
            }
        }
        return 1;
    }

    public void updateDocument(Connection conn, String docId, String newTitle, String newContent, String editor) throws SQLException {
        // Step 1: Fetch the current version of the document and lock the row using FOR UPDATE
        String selectSql = "SELECT title, content FROM documents WHERE doc_id = ? FOR UPDATE";
        String insertHistorySql = "INSERT INTO document_history (doc_id, version_number, old_title, old_content, changed_by) VALUES (?, ?, ?, ?, ?)";
        String updateDocSql = "UPDATE documents SET title = ?, content = ?, last_updated_by = ? WHERE doc_id = ?";

        String oldTitle = null;
        String oldContent = null;

        try (PreparedStatement selectStmt = conn.prepareStatement(selectSql)) {
            selectStmt.setString(1, docId);
            try (ResultSet rs = selectStmt.executeQuery()) {
                if (rs.next()) {
                    oldTitle = rs.getString("title");
                    oldContent = rs.getString("content");
                } else {
                    throw new SQLException("Document not found!");
                }
            }
        }

        // Step 2: Get the next version number and save the old version to the history table
        int versionNumber = getNextVersionNumber(conn, docId);
        try (PreparedStatement historyStmt = conn.prepareStatement(insertHistorySql)) {
            historyStmt.setString(1, docId);
            historyStmt.setInt(2, versionNumber);
            historyStmt.setString(3, oldTitle);
            historyStmt.setString(4, oldContent);
            historyStmt.setString(5, editor); // The person making the change
            historyStmt.executeUpdate();
        }

        // Step 3: Update the actual document
        try (PreparedStatement updateStmt = conn.prepareStatement(updateDocSql)) {
            updateStmt.setString(1, newTitle);
            updateStmt.setString(2, newContent);
            updateStmt.setString(3, editor);
            updateStmt.setString(4, docId);
            updateStmt.executeUpdate();
        }

        System.out.println("   [VERSIONED] Archived as Version " + versionNumber);
    }

    public void displayHistory(Connection conn, String docId) throws SQLException {
        // Display current document
        String currentSql = "SELECT * FROM documents WHERE doc_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(currentSql)) {
            pstmt.setString(1, docId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    // Count total versions to show current version number
                    int totalVersions = getNextVersionNumber(conn, docId);
                    System.out.println("\n--- Current Version (v" + totalVersions + " - Live) ---");
                    System.out.println("Doc ID: " + rs.getString("doc_id"));
                    System.out.println("Title: " + rs.getString("title"));
                    System.out.println("Content: " + rs.getString("content"));
                    System.out.println("Last Updated By: " + rs.getString("last_updated_by") + " at " + rs.getTimestamp("last_updated_at"));
                }
            }
        }

        // Display history trail with version numbers
        String historySql = "SELECT * FROM document_history WHERE doc_id = ? ORDER BY version_number DESC";
        try (PreparedStatement pstmt = conn.prepareStatement(historySql)) {
            pstmt.setString(1, docId);
            try (ResultSet rs = pstmt.executeQuery()) {
                System.out.println("\n--- Version History Trail (Newest to Oldest) ---");
                while (rs.next()) {
                    int version = rs.getInt("version_number");
                    System.out.println("[v" + version + "] Saved by: " + rs.getString("changed_by") + " on " + rs.getTimestamp("changed_at"));
                    System.out.println("  Title: " + rs.getString("old_title"));
                    System.out.println("  Content: " + rs.getString("old_content"));
                    System.out.println("  -------------------------");
                }
            }
        }
    }
}
