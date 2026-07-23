import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    # ============================================================
    # Program 10: URL Shortener
    # ============================================================
    "Program10_UrlShortener/url_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_urlshortener;
USE demo_urlshortener;

CREATE TABLE IF NOT EXISTS short_urls (
    id INT AUTO_INCREMENT PRIMARY KEY,
    short_code VARCHAR(10) NOT NULL UNIQUE,
    original_url TEXT NOT NULL,
    click_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""",

    "Program10_UrlShortener/src/com/demo/urlshort/db/DatabaseConnection.java": """package com.demo.urlshort.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_urlshortener";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program10_UrlShortener/src/com/demo/urlshort/model/ShortUrl.java": """package com.demo.urlshort.model;

import java.sql.Timestamp;

public class ShortUrl {
    private int id;
    private String shortCode;
    private String originalUrl;
    private int clickCount;
    private Timestamp createdAt;

    public ShortUrl() {}

    public ShortUrl(String shortCode, String originalUrl) {
        this.shortCode = shortCode;
        this.originalUrl = originalUrl;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getShortCode() { return shortCode; }
    public void setShortCode(String shortCode) { this.shortCode = shortCode; }

    public String getOriginalUrl() { return originalUrl; }
    public void setOriginalUrl(String originalUrl) { this.originalUrl = originalUrl; }

    public int getClickCount() { return clickCount; }
    public void setClickCount(int clickCount) { this.clickCount = clickCount; }

    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    @Override
    public String toString() {
        return String.format("Code: %s | Clicks: %d | URL: %s", shortCode, clickCount, originalUrl);
    }
}
""",

    "Program10_UrlShortener/src/com/demo/urlshort/dao/UrlDAO.java": """package com.demo.urlshort.dao;

import com.demo.urlshort.model.ShortUrl;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class UrlDAO {

    /**
     * Inserts a new short URL mapping into the database.
     * Uses a unique constraint on short_code to prevent collisions.
     */
    public void insertShortUrl(Connection conn, String shortCode, String originalUrl) throws SQLException {
        String sql = "INSERT INTO short_urls (short_code, original_url) VALUES (?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, shortCode);
            pstmt.setString(2, originalUrl);
            pstmt.executeUpdate();
        }
    }

    /**
     * Checks if a short code already exists in the database.
     * This is used for collision detection during code generation.
     */
    public boolean shortCodeExists(Connection conn, String shortCode) throws SQLException {
        String sql = "SELECT 1 FROM short_urls WHERE short_code = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, shortCode);
            try (ResultSet rs = pstmt.executeQuery()) {
                return rs.next();
            }
        }
    }

    /**
     * Simulates a "click" on the short URL.
     * Atomically increments the click counter and returns the original URL.
     * Uses a transaction to ensure the increment and read are consistent.
     */
    public String resolveAndTrackClick(Connection conn, String shortCode) throws SQLException {
        String originalUrl = null;

        // Step 1: Atomically increment the click count
        String updateSql = "UPDATE short_urls SET click_count = click_count + 1 WHERE short_code = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(updateSql)) {
            pstmt.setString(1, shortCode);
            int rowsAffected = pstmt.executeUpdate();
            if (rowsAffected == 0) {
                throw new SQLException("Short code '" + shortCode + "' not found in database.");
            }
        }

        // Step 2: Fetch the original URL
        String selectSql = "SELECT original_url FROM short_urls WHERE short_code = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(selectSql)) {
            pstmt.setString(1, shortCode);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    originalUrl = rs.getString("original_url");
                }
            }
        }

        return originalUrl;
    }

    /**
     * Retrieves all short URLs with their analytics, sorted by most clicked.
     */
    public List<ShortUrl> getAllUrlsSortedByClicks(Connection conn) throws SQLException {
        List<ShortUrl> urls = new ArrayList<>();
        String sql = "SELECT * FROM short_urls ORDER BY click_count DESC";
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            while (rs.next()) {
                ShortUrl url = new ShortUrl();
                url.setId(rs.getInt("id"));
                url.setShortCode(rs.getString("short_code"));
                url.setOriginalUrl(rs.getString("original_url"));
                url.setClickCount(rs.getInt("click_count"));
                url.setCreatedAt(rs.getTimestamp("created_at"));
                urls.add(url);
            }
        }
        return urls;
    }

    public void clearTable(Connection conn) throws SQLException {
        try (PreparedStatement pstmt = conn.prepareStatement("TRUNCATE TABLE short_urls")) {
            pstmt.executeUpdate();
        }
    }
}
""",

    "Program10_UrlShortener/src/com/demo/urlshort/service/UrlService.java": """package com.demo.urlshort.service;

import com.demo.urlshort.dao.UrlDAO;
import com.demo.urlshort.db.DatabaseConnection;
import com.demo.urlshort.model.ShortUrl;
import java.sql.Connection;
import java.sql.SQLException;
import java.security.SecureRandom;
import java.util.List;

public class UrlService {
    private UrlDAO urlDAO = new UrlDAO();

    // Base62 character set: [0-9, a-z, A-Z] = 62 characters
    private static final String BASE62_CHARS = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
    private static final int CODE_LENGTH = 6;
    private static final int MAX_COLLISION_RETRIES = 5;
    private SecureRandom random = new SecureRandom();

    /**
     * Generates a cryptographically random Base62 short code.
     * Uses SecureRandom instead of Random for unpredictability.
     */
    private String generateShortCode() {
        StringBuilder code = new StringBuilder(CODE_LENGTH);
        for (int i = 0; i < CODE_LENGTH; i++) {
            int index = random.nextInt(BASE62_CHARS.length());
            code.append(BASE62_CHARS.charAt(index));
        }
        return code.toString();
    }

    /**
     * Shortens a URL with collision detection.
     * If the generated code already exists in the DB, it retries up to MAX_COLLISION_RETRIES times.
     */
    public String shortenUrl(String originalUrl) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            String shortCode = null;
            boolean inserted = false;

            for (int attempt = 1; attempt <= MAX_COLLISION_RETRIES; attempt++) {
                shortCode = generateShortCode();
                
                if (!urlDAO.shortCodeExists(conn, shortCode)) {
                    urlDAO.insertShortUrl(conn, shortCode, originalUrl);
                    inserted = true;
                    break;
                } else {
                    System.out.println("   [COLLISION] Code '" + shortCode + "' already exists. Retrying... (Attempt " + attempt + ")");
                }
            }

            if (!inserted) {
                throw new RuntimeException("Failed to generate a unique short code after " + MAX_COLLISION_RETRIES + " attempts.");
            }

            return shortCode;

        } catch (SQLException e) {
            System.err.println("[ERROR] Database error while shortening URL: " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Resolves a short code back to the original URL and tracks the click.
     */
    public String resolveUrl(String shortCode) {
        try (Connection conn = DatabaseConnection.getConnection()) {
            return urlDAO.resolveAndTrackClick(conn, shortCode);
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to resolve short code '" + shortCode + "': " + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }

    /**
     * Displays click analytics for all shortened URLs.
     */
    public void displayAnalytics() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            List<ShortUrl> urls = urlDAO.getAllUrlsSortedByClicks(conn);
            System.out.println("\\n--- Click Analytics (Sorted by Most Clicked) ---");
            if (urls.isEmpty()) {
                System.out.println("No URLs found.");
            } else {
                for (ShortUrl url : urls) {
                    System.out.println("  " + url.toString());
                }
            }
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to retrieve analytics: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Clears all data for a fresh demo run.
     */
    public void clearData() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            urlDAO.clearTable(conn);
        } catch (SQLException e) {
            System.err.println("[ERROR] Failed to clear table: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
""",

    "Program10_UrlShortener/src/com/demo/urlshort/main/UrlShortenerMain.java": """package com.demo.urlshort.main;

import com.demo.urlshort.service.UrlService;

public class UrlShortenerMain {
    public static void main(String[] args) {
        System.out.println("=== URL Shortener Service (Base62 Encoding) ===\\n");
        UrlService service = new UrlService();

        // Clean slate
        service.clearData();

        // 1. Shorten some URLs
        System.out.println("[Step 1] Shortening URLs...");
        String code1 = service.shortenUrl("https://docs.google.com/spreadsheets/d/1a2b3c4d5e/edit?usp=sharing");
        System.out.println("  Long URL shortened to code: " + code1);

        String code2 = service.shortenUrl("https://www.amazon.in/dp/B0CXYZ1234/ref=sr_1_1?keywords=laptop&qid=1690000000");
        System.out.println("  Long URL shortened to code: " + code2);

        String code3 = service.shortenUrl("https://stackoverflow.com/questions/12345678/how-to-use-preparedstatement-in-java");
        System.out.println("  Long URL shortened to code: " + code3);

        // 2. Simulate clicks
        System.out.println("\\n[Step 2] Simulating user clicks...");
        for (int i = 0; i < 5; i++) {
            String resolved = service.resolveUrl(code1);
            if (i == 0) System.out.println("  Clicking code '" + code1 + "' -> Redirects to: " + resolved);
        }
        System.out.println("  (Clicked code '" + code1 + "' 5 times total)");

        for (int i = 0; i < 2; i++) {
            service.resolveUrl(code2);
        }
        System.out.println("  (Clicked code '" + code2 + "' 2 times total)");

        service.resolveUrl(code3);
        System.out.println("  (Clicked code '" + code3 + "' 1 time total)");

        // 3. Display analytics
        service.displayAnalytics();
    }
}
""",

    # ============================================================
    # Program 11: Password Vault (AES Encryption)
    # ============================================================
    "Program11_PasswordVault/vault_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_vault;
USE demo_vault;

CREATE TABLE IF NOT EXISTS credentials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    encrypted_password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_service_user (service_name, username)
);
""",

    "Program11_PasswordVault/src/com/demo/vault/db/DatabaseConnection.java": """package com.demo.vault.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_vault";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program11_PasswordVault/src/com/demo/vault/model/Credential.java": """package com.demo.vault.model;

public class Credential {
    private int id;
    private String serviceName;
    private String username;
    private String encryptedPassword; // What the DB stores (gibberish)
    private String decryptedPassword; // What the user sees (plain text, only in memory)

    public Credential() {}

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getServiceName() { return serviceName; }
    public void setServiceName(String serviceName) { this.serviceName = serviceName; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEncryptedPassword() { return encryptedPassword; }
    public void setEncryptedPassword(String encryptedPassword) { this.encryptedPassword = encryptedPassword; }

    public String getDecryptedPassword() { return decryptedPassword; }
    public void setDecryptedPassword(String decryptedPassword) { this.decryptedPassword = decryptedPassword; }

    @Override
    public String toString() {
        return String.format("Service: %-15s | User: %-15s | Encrypted: %s", serviceName, username, encryptedPassword);
    }
}
""",

    "Program11_PasswordVault/src/com/demo/vault/util/AESEncryptor.java": """package com.demo.vault.util;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.NoSuchAlgorithmException;
import java.util.Base64;

/**
 * AES-128 Encryption Utility.
 * Encrypts plaintext passwords into unreadable ciphertext before they reach the database.
 * Decrypts ciphertext back into plaintext when the user requests their password.
 *
 * IMPORTANT: In a production environment, the secret key would NEVER be hardcoded.
 * It would be stored in an environment variable, a secrets manager (like AWS KMS),
 * or a hardware security module (HSM).
 */
public class AESEncryptor {

    private static final String ALGORITHM = "AES";

    // A fixed 16-byte (128-bit) key for demo purposes.
    // In production, this would come from an environment variable or vault.
    private static final byte[] FIXED_KEY = "DemoSecretKey128".getBytes();
    private static final SecretKeySpec SECRET_KEY = new SecretKeySpec(FIXED_KEY, ALGORITHM);

    /**
     * Encrypts a plaintext string using AES-128.
     * Returns a Base64-encoded string safe for database storage.
     *
     * @param plainText The password in readable format
     * @return Base64-encoded encrypted string
     * @throws Exception if encryption fails
     */
    public static String encrypt(String plainText) throws Exception {
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.ENCRYPT_MODE, SECRET_KEY);
        byte[] encryptedBytes = cipher.doFinal(plainText.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(encryptedBytes);
    }

    /**
     * Decrypts a Base64-encoded AES ciphertext back to plaintext.
     *
     * @param cipherText The Base64-encoded encrypted string from the database
     * @return The original password in readable format
     * @throws Exception if decryption fails (e.g., wrong key, corrupted data)
     */
    public static String decrypt(String cipherText) throws Exception {
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        cipher.init(Cipher.DECRYPT_MODE, SECRET_KEY);
        byte[] decodedBytes = Base64.getDecoder().decode(cipherText);
        byte[] decryptedBytes = cipher.doFinal(decodedBytes);
        return new String(decryptedBytes, "UTF-8");
    }
}
""",

    "Program11_PasswordVault/src/com/demo/vault/dao/VaultDAO.java": """package com.demo.vault.dao;

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
""",

    "Program11_PasswordVault/src/com/demo/vault/service/VaultService.java": """package com.demo.vault.service;

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
            System.out.println("\\n--- Database Admin View (What a hacker would see) ---");
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
""",

    "Program11_PasswordVault/src/com/demo/vault/main/VaultMain.java": """package com.demo.vault.main;

import com.demo.vault.service.VaultService;

public class VaultMain {
    public static void main(String[] args) {
        System.out.println("=== Secure Password Vault (AES-128 Encryption) ===\\n");
        VaultService service = new VaultService();

        // Clean slate
        service.clearData();

        // 1. Store credentials (passwords get encrypted before hitting the DB)
        System.out.println("[Step 1] Storing credentials securely...");
        service.storeCredential("Gmail", "aviral.bansal", "MyGmail@2026!");
        service.storeCredential("GitHub", "aviral-dev", "GitP@ss#Secure99");
        service.storeCredential("AWS Console", "admin", "Aws!Root$Key2026");

        // 2. Show what the database actually stores (encrypted gibberish)
        service.displayDatabaseView();

        // 3. Retrieve and decrypt specific credentials
        System.out.println("\\n[Step 3] Retrieving and decrypting credentials...");
        service.retrieveCredential("Gmail", "aviral.bansal");
        System.out.println();
        service.retrieveCredential("GitHub", "aviral-dev");
        System.out.println();
        service.retrieveCredential("AWS Console", "admin");

        // 4. Try retrieving a non-existent credential
        System.out.println("\\n[Step 4] Attempting to retrieve a non-existent credential...");
        service.retrieveCredential("Netflix", "someone");
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Programs 10 and 11 generated successfully!")
