package com.demo.vault.service;

import com.demo.vault.dao.VaultDAO;
import com.demo.vault.db.DatabaseConnection;
import com.demo.vault.model.Credential;
import com.demo.vault.util.AESEncryptor;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

public class VaultService {
    private VaultDAO vaultDAO = new VaultDAO();

    /**
     * Stores a new credential. The password is encrypted in the service layer
     * BEFORE it is ever handed to the DAO or touches the database.
     */
    public void storeCredential(String serviceName, String username, String plainPassword) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            // Encrypt BEFORE touching the database
            String encrypted = AESEncryptor.encrypt(plainPassword);
            System.out.println("  [ENCRYPT] '" + plainPassword + "' -> '" + encrypted + "'");

            vaultDAO.saveCredential(conn, serviceName, username, encrypted);
            System.out.println("  [STORED]  Credential saved to database for " + serviceName);

        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to store credential: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("[CRYPTO ERROR] Encryption failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Retrieves and decrypts a credential from the database.
     * Decryption happens in the service layer AFTER retrieval, never in SQL.
     */
    public void retrieveCredential(String serviceName, String username) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            Credential cred = vaultDAO.getCredential(conn, serviceName, username);

            if (cred == null) {
                System.out.println("  [NOT FOUND] No credential found for " + serviceName + " / " + username);
                return;
            }

            // Decrypt AFTER retrieving from database
            String decrypted = AESEncryptor.decrypt(cred.getEncryptedPassword());
            cred.setDecryptedPassword(decrypted);

            System.out.println("  [RETRIEVED] " + cred.getServiceName() + " / " + cred.getUsername());
            System.out.println("  [DB VALUE]  Encrypted: " + cred.getEncryptedPassword());
            System.out.println("  [DECRYPT]   Decrypted: " + cred.getDecryptedPassword());

        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to retrieve credential: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("[CRYPTO ERROR] Decryption failed: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Displays what a database administrator or hacker would see.
     * They can access the database, but all passwords are gibberish.
     */
    public void displayDatabaseView() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            List<Credential> creds = vaultDAO.getAllCredentials(conn);
            System.out.println("\n--- Database Admin View (What a hacker would see) ---");
            if (creds.isEmpty()) {
                System.out.println("  No credentials stored.");
            } else {
                for (Credential cred : creds) {
                    System.out.println("  " + cred.toString());
                }
            }
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to display credentials: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Clears all data for a fresh demo run.
     */
    public void clearData() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            vaultDAO.clearTable(conn);
        } catch (SQLException e) {
            System.err.println("[DB ERROR] Failed to clear vault: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
