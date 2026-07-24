CREATE DATABASE IF NOT EXISTS demo_ratelimiter;
USE demo_ratelimiter;

CREATE TABLE IF NOT EXISTS rate_limit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    requested_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_user_endpoint_time (user_id, endpoint, requested_at)
);
