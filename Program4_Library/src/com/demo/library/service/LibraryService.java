package com.demo.library.service;

import com.demo.library.dao.LibraryDAO;
import com.demo.library.db.DatabaseConnection;
import com.demo.library.model.Book;
import java.sql.Connection;
import java.sql.SQLException;

public class LibraryService {
    private LibraryDAO libraryDAO = new LibraryDAO();

    public void displayBookStatus(int bookId) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            Book book = libraryDAO.getBookById(conn, bookId);
            if (book != null) {
                System.out.println(book);
            } else {
                System.out.println("Book not found.");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    public void borrowBook(int bookId, String memberName) {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            conn.setAutoCommit(false);

            boolean success = libraryDAO.checkoutBook(conn, bookId, memberName);
            if (success) {
                conn.commit();
                System.out.println(memberName + " successfully borrowed Book ID " + bookId);
            } else {
                conn.rollback();
                System.out.println("Checkout failed for Book ID " + bookId + ". No copies available.");
            }
        } catch (SQLException e) {
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
