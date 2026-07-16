package com.demo.iot.service;

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
