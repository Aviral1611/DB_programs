import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    # Program 5: API Cache
    "Program5_ApiCache/api_cache_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_apicache;
USE demo_apicache;

CREATE TABLE IF NOT EXISTS api_cache (
    endpoint VARCHAR(255) PRIMARY KEY,
    response TEXT NOT NULL,
    timestamp_ms BIGINT NOT NULL
);
""",

    "Program5_ApiCache/src/com/demo/apicache/db/DatabaseConnection.java": """package com.demo.apicache.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_apicache";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program5_ApiCache/src/com/demo/apicache/model/CacheEntry.java": """package com.demo.apicache.model;

public class CacheEntry {
    private String endpoint;
    private String response;
    private long timestampMs;

    public CacheEntry(String endpoint, String response, long timestampMs) {
        this.endpoint = endpoint;
        this.response = response;
        this.timestampMs = timestampMs;
    }

    public String getEndpoint() { return endpoint; }
    public String getResponse() { return response; }
    public long getTimestampMs() { return timestampMs; }
}
""",

    "Program5_ApiCache/src/com/demo/apicache/dao/ApiCacheDAO.java": """package com.demo.apicache.dao;

import com.demo.apicache.model.CacheEntry;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class ApiCacheDAO {
    public CacheEntry getCacheByEndpoint(Connection conn, String endpoint) throws SQLException {
        String sql = "SELECT * FROM api_cache WHERE endpoint = ?";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, endpoint);
            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    return new CacheEntry(
                        rs.getString("endpoint"),
                        rs.getString("response"),
                        rs.getLong("timestamp_ms")
                    );
                }
            }
        }
        return null;
    }

    public void saveOrUpdateCache(Connection conn, String endpoint, String response, long timestampMs) throws SQLException {
        String sql = "INSERT INTO api_cache (endpoint, response, timestamp_ms) VALUES (?, ?, ?) " +
                     "ON DUPLICATE KEY UPDATE response = VALUES(response), timestamp_ms = VALUES(timestamp_ms)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, endpoint);
            pstmt.setString(2, response);
            pstmt.setLong(3, timestampMs);
            pstmt.executeUpdate();
        }
    }
}
""",

    "Program5_ApiCache/src/com/demo/apicache/service/ApiService.java": """package com.demo.apicache.service;

import com.demo.apicache.dao.ApiCacheDAO;
import com.demo.apicache.db.DatabaseConnection;
import com.demo.apicache.model.CacheEntry;
import com.github.benmanes.caffeine.cache.Cache;
import com.github.benmanes.caffeine.cache.Caffeine;
import java.sql.Connection;
import java.sql.SQLException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.concurrent.TimeUnit;

public class ApiService {
    private ApiCacheDAO cacheDAO = new ApiCacheDAO();
    private static final long CACHE_EXPIRY_MS = 5 * 60 * 1000; // 5 minutes for Database expiration
    
    // L1 Cache (In-Memory RAM) using Caffeine
    private Cache<String, String> l1Cache = Caffeine.newBuilder()
            .expireAfterWrite(5, TimeUnit.MINUTES) // Auto-expires data in RAM after 5 minutes
            .maximumSize(1000) // Keep at most 1000 endpoints in RAM to save memory
            .build();

    public String getData(String endpoint) {
        // Step 1: Check L1 Cache (RAM)
        String ramData = l1Cache.getIfPresent(endpoint);
        if (ramData != null) {
            System.out.println(">>> [L1 CACHE HIT] Serving from Caffeine RAM Cache (0.1ms)");
            return ramData;
        }
        
        System.out.println(">>> [L1 CACHE MISS] Checking Database (L2)...");

        // Step 2: Check L2 Cache (Database)
        try (Connection conn = DatabaseConnection.getConnection()) {
            CacheEntry dbCache = cacheDAO.getCacheByEndpoint(conn, endpoint);
            long currentTime = System.currentTimeMillis();

            if (dbCache != null && (currentTime - dbCache.getTimestampMs()) < CACHE_EXPIRY_MS) {
                System.out.println(">>> [L2 CACHE HIT] Serving from MySQL Database (2-5ms)");
                // Promote back up to L1
                l1Cache.put(endpoint, dbCache.getResponse());
                return dbCache.getResponse();
            }

            System.out.println(">>> [L2 CACHE MISS / EXPIRED] Fetching from External API (L3)...");
            
            // Step 3: Fetch from L3 (Network API)
            String freshData = fetchFromNetwork(endpoint);
            
            // Save to L2 (Database)
            cacheDAO.saveOrUpdateCache(conn, endpoint, freshData, currentTime);
            
            // Save to L1 (RAM)
            l1Cache.put(endpoint, freshData);
            
            return freshData;

        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    private String fetchFromNetwork(String targetUrl) throws Exception {
        URL url = new URL(targetUrl);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        StringBuilder result = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                result.append(line);
            }
        }
        return result.toString();
    }
}
""",

    "Program5_ApiCache/src/com/demo/apicache/main/ApiCacheMain.java": """package com.demo.apicache.main;

import com.demo.apicache.service.ApiService;

public class ApiCacheMain {
    public static void main(String[] args) {
        System.out.println("=== API Caching System (L1 + L2 Architecture) ===");
        ApiService service = new ApiService();
        String apiUrl = "https://api.agify.io?name=java";

        System.out.println("\\n[Request 1 - Cold Start]");
        String result1 = service.getData(apiUrl);

        System.out.println("\\n[Request 2 - Immediate follow-up]");
        String result2 = service.getData(apiUrl);
        
        System.out.println("\\nNote: To see an L2 Database hit, you would typically restart this application.");
        System.out.println("Because the RAM cache (L1) is destroyed on exit, but the Database (L2) persists,");
        System.out.println("the next time you run this, Request 1 will be an [L2 CACHE HIT]!");
    }
}
""",

    # Program 6: JSON to Relational
    "Program6_JsonRelational/json_relational_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_jsonrel;
USE demo_jsonrel;

CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS user_hobbies (
    hobby_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    hobby VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);
""",

    "Program6_JsonRelational/src/com/demo/jsonrel/db/DatabaseConnection.java": """package com.demo.jsonrel.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_jsonrel";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program6_JsonRelational/src/com/demo/jsonrel/model/User.java": """package com.demo.jsonrel.model;

import java.util.List;

public class User {
    private int id;
    private String name;
    private List<String> hobbies;

    public User() {}

    public User(int id, String name, List<String> hobbies) {
        this.id = id;
        this.name = name;
        this.hobbies = hobbies;
    }

    public int getId() { return id; }
    public String getName() { return name; }
    public List<String> getHobbies() { return hobbies; }
}
""",

    "Program6_JsonRelational/src/com/demo/jsonrel/dao/UserDAO.java": """package com.demo.jsonrel.dao;

import com.demo.jsonrel.model.User;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class UserDAO {
    public void insertUserWithHobbies(Connection conn, User user) throws SQLException {
        String insertUserSql = "INSERT INTO users (user_id, name) VALUES (?, ?) ON DUPLICATE KEY UPDATE name = VALUES(name)";
        String insertHobbySql = "INSERT INTO user_hobbies (user_id, hobby) VALUES (?, ?)";

        try (PreparedStatement userStmt = conn.prepareStatement(insertUserSql)) {
            userStmt.setInt(1, user.getId());
            userStmt.setString(2, user.getName());
            userStmt.executeUpdate();
        }

        try (PreparedStatement hobbyStmt = conn.prepareStatement(insertHobbySql)) {
            for (String hobby : user.getHobbies()) {
                hobbyStmt.setInt(1, user.getId());
                hobbyStmt.setString(2, hobby);
                hobbyStmt.executeUpdate();
            }
        }
    }

    public void displayAllUsersAndHobbies(Connection conn) throws SQLException {
        String sql = "SELECT u.name, h.hobby FROM users u JOIN user_hobbies h ON u.user_id = h.user_id ORDER BY u.name";
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
            
            String currentUser = "";
            while (rs.next()) {
                String name = rs.getString("name");
                String hobby = rs.getString("hobby");

                if (!name.equals(currentUser)) {
                    System.out.println("\\nUser: " + name);
                    currentUser = name;
                }
                System.out.println("  - Hobby: " + hobby);
            }
        }
    }

    public void clearTables(Connection conn) throws SQLException {
        conn.createStatement().execute("DELETE FROM user_hobbies");
        conn.createStatement().execute("DELETE FROM users");
    }
}
""",

    "Program6_JsonRelational/src/com/demo/jsonrel/service/JsonService.java": """package com.demo.jsonrel.service;

import com.demo.jsonrel.dao.UserDAO;
import com.demo.jsonrel.db.DatabaseConnection;
import com.demo.jsonrel.model.User;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.sql.Connection;
import java.sql.SQLException;
import java.util.List;

public class JsonService {
    private UserDAO userDAO = new UserDAO();
    private ObjectMapper mapper = new ObjectMapper();

    public void processJsonToDatabase(String jsonPayload) {
        Connection conn = null;
        try {
            conn = DatabaseConnection.getConnection();
            conn.setAutoCommit(false);
            
            userDAO.clearTables(conn);

            // Using Jackson for robust JSON parsing
            List<User> users = mapper.readValue(jsonPayload, new TypeReference<List<User>>() {});

            for (User user : users) {
                userDAO.insertUserWithHobbies(conn, user);
            }

            conn.commit();
            System.out.println("Successfully parsed JSON using Jackson and inserted into relational tables.");
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

    public void showNormalizedData() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            System.out.println("\\n[Current Relational Data from DB]");
            userDAO.displayAllUsersAndHobbies(conn);
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
""",

    "Program6_JsonRelational/src/com/demo/jsonrel/main/JsonRelationalMain.java": """package com.demo.jsonrel.main;

import com.demo.jsonrel.service.JsonService;

public class JsonRelationalMain {
    public static void main(String[] args) {
        System.out.println("=== JSON to Relational DB Converter ===");
        JsonService service = new JsonService();

        // Standard JSON format with double quotes (escaped for Java String)
        String jsonPayload = 
            "[{\\\"id\\\":1, \\\"name\\\":\\\"Alice\\\", \\\"hobbies\\\":[\\\"reading\\\",\\\"hiking\\\"]}, " +
            "{\\\"id\\\":2, \\\"name\\\":\\\"Bob\\\", \\\"hobbies\\\":[\\\"gaming\\\"]}, " +
            "{\\\"id\\\":3, \\\"name\\\":\\\"Charlie\\\", \\\"hobbies\\\":[\\\"cooking\\\",\\\"traveling\\\",\\\"swimming\\\"]}]";

        System.out.println("Raw JSON Payload: " + jsonPayload + "\\n");

        service.processJsonToDatabase(jsonPayload);
        service.showNormalizedData();
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Programs 5 and 6 generated successfully!")
