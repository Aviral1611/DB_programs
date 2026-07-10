package com.demo.bank.service;

import com.demo.bank.dao.AccountDAO;
import com.demo.bank.db.DatabaseConnection;
import com.demo.bank.model.Account;

import java.sql.Connection;
import java.sql.SQLException;

public class BankService {
    private AccountDAO accountDAO;

    public BankService() {
        this.accountDAO = new AccountDAO();
    }

    /**
     * Demonstrates a transaction using ACID properties.
     * We disable auto-commit, perform two updates, and then commit.
     * If anything fails, we rollback the entire transaction.
     */
    public boolean transferFunds(int fromAccountId, int toAccountId, double amount) {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            // Start transaction
            conn.setAutoCommit(false);
            System.out.println("Transaction started...");

            Account fromAccount = accountDAO.getAccountById(conn, fromAccountId);
            Account toAccount = accountDAO.getAccountById(conn, toAccountId);

            if (fromAccount == null || toAccount == null) {
                System.out.println("One or both accounts do not exist. Transfer failed.");
                conn.rollback();
                return false;
            }

            if (fromAccount.getBalance() < amount) {
                System.out.println("Insufficient funds in Account " + fromAccountId + ". Transfer failed.");
                conn.rollback();
                return false;
            }

            // Deduct from sender
            double newFromBalance = fromAccount.getBalance() - amount;
            accountDAO.updateBalance(conn, fromAccountId, newFromBalance);
            
            // Add to receiver
            double newToBalance = toAccount.getBalance() + amount;
            accountDAO.updateBalance(conn, toAccountId, newToBalance);

            // Commit transaction
            conn.commit();
            System.out.println("Transfer of $" + amount + " successful! Transaction committed.");
            return true;

        } catch (SQLException e) {
            System.err.println("SQL Error occurred. Rolling back transaction...");
            if (conn != null) {
                try {
                    conn.rollback();
                } catch (SQLException ex) {
                    ex.printStackTrace();
                }
            }
            e.printStackTrace();
            return false;
        } finally {
            if (conn != null) {
                try {
                    // Reset auto-commit and close connection
                    conn.setAutoCommit(true);
                    conn.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }
    }
    
    public void printAccountDetails(int accountId) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            Account acc = accountDAO.getAccountById(conn, accountId);
            if (acc != null) {
                System.out.println(acc);
            } else {
                System.out.println("Account " + accountId + " not found.");
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
