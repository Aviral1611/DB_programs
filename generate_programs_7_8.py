import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    # Program 7: IoT Sensor Data Aggregator
    "Program7_IotAggregator/iot_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_iot;
USE demo_iot;

CREATE TABLE IF NOT EXISTS raw_sensor_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    temperature DECIMAL(5,2) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS hourly_aggregates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sensor_id VARCHAR(50) NOT NULL,
    hour_bucket TIMESTAMP NOT NULL,
    avg_temp DECIMAL(5,2),
    max_temp DECIMAL(5,2),
    min_temp DECIMAL(5,2),
    UNIQUE KEY unique_sensor_hour (sensor_id, hour_bucket)
);
""",

    "Program7_IotAggregator/src/com/demo/iot/db/DatabaseConnection.java": """package com.demo.iot.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_iot";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program7_IotAggregator/src/com/demo/iot/dao/SensorDAO.java": """package com.demo.iot.dao;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;

public class SensorDAO {
    
    public void insertRawData(Connection conn, String sensorId, double temperature, Timestamp recordedAt) throws SQLException {
        String sql = "INSERT INTO raw_sensor_data (sensor_id, temperature, recorded_at) VALUES (?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setString(1, sensorId);
            pstmt.setDouble(2, temperature);
            pstmt.setTimestamp(3, recordedAt);
            pstmt.executeUpdate();
        }
    }

    public void runAggregationBatch(Connection conn) throws SQLException {
        // This query groups raw data by sensor and by the hour, calculates stats, 
        // and inserts/updates the aggregate table in bulk directly in the DB engine!
        String sql = 
            "INSERT INTO hourly_aggregates (sensor_id, hour_bucket, avg_temp, max_temp, min_temp) " +
            "SELECT " +
            "   sensor_id, " +
            "   DATE_FORMAT(recorded_at, '%Y-%m-%d %H:00:00') as hour_bucket, " +
            "   AVG(temperature), " +
            "   MAX(temperature), " +
            "   MIN(temperature) " +
            "FROM raw_sensor_data " +
            "GROUP BY sensor_id, hour_bucket " +
            "ON DUPLICATE KEY UPDATE " +
            "   avg_temp = VALUES(avg_temp), " +
            "   max_temp = VALUES(max_temp), " +
            "   min_temp = VALUES(min_temp)";

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Batch Aggregation Complete. Aggregate rows inserted/updated: " + rowsAffected);
        }
    }

    public void displayAggregates(Connection conn) throws SQLException {
        String sql = "SELECT * FROM hourly_aggregates ORDER BY hour_bucket DESC, sensor_id ASC";
        try (PreparedStatement pstmt = conn.prepareStatement(sql);
             ResultSet rs = pstmt.executeQuery()) {
             
            System.out.println("\\n--- Hourly Aggregated Metrics ---");
            while (rs.next()) {
                System.out.printf("Sensor: %s | Time: %s | Avg: %.2f | Max: %.2f | Min: %.2f\\n",
                    rs.getString("sensor_id"),
                    rs.getTimestamp("hour_bucket"),
                    rs.getDouble("avg_temp"),
                    rs.getDouble("max_temp"),
                    rs.getDouble("min_temp")
                );
            }
        }
    }
    
    public void clearTables(Connection conn) throws SQLException {
        conn.createStatement().execute("TRUNCATE TABLE raw_sensor_data");
        conn.createStatement().execute("TRUNCATE TABLE hourly_aggregates");
    }
}
""",

    "Program7_IotAggregator/src/com/demo/iot/service/IotService.java": """package com.demo.iot.service;

import com.demo.iot.dao.SensorDAO;
import com.demo.iot.db.DatabaseConnection;
import java.sql.Connection;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.util.Random;

public class IotService {
    private SensorDAO sensorDAO = new SensorDAO();

    public void simulateAndAggregate() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            sensorDAO.clearTables(conn);
            
            System.out.println("Simulating 100 raw sensor readings...");
            Random rand = new Random();
            long currentTime = System.currentTimeMillis();
            
            // Simulate data for 2 sensors over the last 2 hours
            for (int i = 0; i < 100; i++) {
                String sensorId = (i % 2 == 0) ? "SENSOR_A" : "SENSOR_B";
                // Random temp between 20.0 and 30.0
                double temp = 20.0 + (rand.nextDouble() * 10);
                // Random time within the last 2 hours
                long timeOffset = (long) (rand.nextDouble() * 2 * 60 * 60 * 1000);
                Timestamp timestamp = new Timestamp(currentTime - timeOffset);
                
                sensorDAO.insertRawData(conn, sensorId, temp, timestamp);
            }
            System.out.println("Raw data inserted successfully.");

            // Run the batch aggregation job
            System.out.println("Running Aggregation Job...");
            sensorDAO.runAggregationBatch(conn);

            // Display results
            sensorDAO.displayAggregates(conn);

        } catch (SQLException e) {
            e.printStackTrace();
        }
    }
}
""",

    "Program7_IotAggregator/src/com/demo/iot/main/IotMain.java": """package com.demo.iot.main;

import com.demo.iot.service.IotService;

public class IotMain {
    public static void main(String[] args) {
        System.out.println("=== IoT Data Aggregator Pipeline ===");
        IotService service = new IotService();
        service.simulateAndAggregate();
    }
}
""",

    # Program 8: Document Audit Trail
    "Program8_AuditTrail/audit_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_audit;
USE demo_audit;

CREATE TABLE IF NOT EXISTS documents (
    doc_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    last_updated_by VARCHAR(100) NOT NULL,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    doc_id INT NOT NULL,
    old_title VARCHAR(255),
    old_content TEXT,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(doc_id) ON DELETE CASCADE
);
""",

    "Program8_AuditTrail/src/com/demo/audit/db/DatabaseConnection.java": """package com.demo.audit.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_audit";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program8_AuditTrail/src/com/demo/audit/dao/DocumentDAO.java": """package com.demo.audit.dao;

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
                    System.out.println("\\n--- Current Version (Live) ---");
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
                System.out.println("\\n--- Version History Trail (Newest to Oldest) ---");
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
""",

    "Program8_AuditTrail/src/com/demo/audit/service/AuditService.java": """package com.demo.audit.service;

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
""",

    "Program8_AuditTrail/src/com/demo/audit/main/AuditMain.java": """package com.demo.audit.main;

import com.demo.audit.service.AuditService;

public class AuditMain {
    public static void main(String[] args) {
        System.out.println("=== Document Version Control & Audit Trail ===");
        AuditService service = new AuditService();
        service.runAuditDemo();
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Programs 7 and 8 generated successfully!")
