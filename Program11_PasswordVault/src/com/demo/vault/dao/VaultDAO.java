package com.demo.vault.dao;

import com.demo.vault.model.Credential;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class VaultDAO {

    /**
     * Stores an encrypted credential in the database.
     * The password is already encrypted BEFORE it reaches the DAO layer.
     */
    public void saveCredential(Connection conn, String serviceName, String username, String encryptedPassword) throws SQLException {
        String sql = "INSERT INTO credentials (service_name, username, encrypted_password) VALUES (?, ?, ?) " +
                     "ON DUPLICATE KEY UPDATE encrypted_password = VALUES(encrypted_password)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, serviceName);
            pstmt.setString(2, username);
            pstmt.setString(3, encryptedPassword);
            pstmt.executeUpdate();
        }
    }

    /**
     * Retrieves a single credential by service name and username.
     * Returns the encrypted password as stored in the database.
     */
    public Credential getCredential(Connection conn, String serviceName, String username) throws SQLException {
        String sql = "SELECT * FROM credentials WHERE service_name = ? AND username = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, serviceName);
            pstmt.setString(2, username);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    Credential cred = new Credential();
                    cred.setId(rs.getInt("id"));
                    cred.setServiceName(rs.getString("service_name"));
                    cred.setUsername(rs.getString("username"));
                    cred.setEncryptedPassword(rs.getString("encrypted_password"));
                    return cred;
                }
            }
        }
        return null;
    }

    /**
     * Retrieves all credentials from the database.
     * All passwords remain in their encrypted form.
     */
    public List<Credential> getAllCredentials(Connection conn) throws SQLException {
        List<Credential> credentials = new ArrayList<>();
        String sql = "SELECT * FROM credentials ORDER BY service_name ASC";
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                Credential cred = new Credential();
                cred.setId(rs.getInt("id"));
                cred.setServiceName(rs.getString("service_name"));
                cred.setUsername(rs.getString("username"));
                cred.setEncryptedPassword(rs.getString("encrypted_password"));
                credentials.add(cred);
            }
        }
        return credentials;
    }

    public void clearTable(Connection conn) throws SQLException {
        try (PreparedStatement pstmt = conn.prepareStatement("TRUNCATE TABLE credentials")) {
            pstmt.executeUpdate();
        }
    }
}
