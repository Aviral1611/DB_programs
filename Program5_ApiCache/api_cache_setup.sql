CREATE DATABASE IF NOT EXISTS demo_apicache;
USE demo_apicache;

CREATE TABLE IF NOT EXISTS api_cache (
    endpoint VARCHAR(255) PRIMARY KEY,
    response TEXT NOT NULL,
    timestamp_ms BIGINT NOT NULL
);
