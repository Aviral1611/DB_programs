package com.demo.ratelimit.db;

import com.demo.ratelimit.util.ConfigLoader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

/**
 * Database connection factory.
 * Reads credentials from config.properties instead of hardcoding them.
 */
public class DatabaseConnection {

    public static Connection getConnection() throws SQLException {
        String url = ConfigLoader.get("db.url");
        String user = ConfigLoader.get("db.user");
        String password = ConfigLoader.get("db.password");
        return DriverManager.getConnection(url, user, password);
    }
}
