package com.demo.library.dao;

import com.demo.library.model.Book;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class LibraryDAO {
    public Book getBookById(Connection conn, int bookId) throws SQLException {
        String sql = "SELECT * FROM books WHERE book_id = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setInt(1, bookId);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return new Book(rs.getInt("book_id"), rs.getString("title"), rs.getInt("available_copies"));
                }
            }
        }
        return null;
    }

    public boolean checkoutBook(Connection conn, int bookId, String memberName) throws SQLException {
        String updateBookSql = "UPDATE books SET available_copies = available_copies - 1 WHERE book_id = ? AND available_copies > 0";
        String insertCheckoutSql = "INSERT INTO checkouts (book_id, member_name) VALUES (?, ?)";

        try (PreparedStatement updateStmt = conn.prepareStatement(updateBookSql)) {
            updateStmt.setInt(1, bookId);
            int rowsAffected = updateStmt.executeUpdate();
            
            if (rowsAffected > 0) {
                try (PreparedStatement insertStmt = conn.prepareStatement(insertCheckoutSql)) {
                    insertStmt.setInt(1, bookId);
                    insertStmt.setString(2, memberName);
                    insertStmt.executeUpdate();
                }
                return true;
            }
        }
        return false;
    }
}
