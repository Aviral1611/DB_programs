package com.demo.iot.dao;

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
             
            System.out.println("\n--- Hourly Aggregated Metrics ---");
            while (rs.next()) {
                System.out.printf("Sensor: %s | Time: %s | Avg: %.2f | Max: %.2f | Min: %.2f\n",
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
