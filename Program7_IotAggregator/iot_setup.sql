CREATE DATABASE IF NOT EXISTS demo_iot;
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
