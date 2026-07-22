import os

base_dir = r"c:\Users\Aviral Bansal\Downloads\Random\Db_programs"

files = {
    "Program9_GeospatialSearch/geo_setup.sql": """CREATE DATABASE IF NOT EXISTS demo_geo;
USE demo_geo;

CREATE TABLE IF NOT EXISTS locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL
);
""",

    "Program9_GeospatialSearch/src/com/demo/geo/db/DatabaseConnection.java": """package com.demo.geo.db;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/demo_geo";
    private static final String USER = "root";
    private static final String PASSWORD = "root";

    public static Connection getConnection() throws SQLException {
        return DriverManager.getConnection(URL, USER, PASSWORD);
    }
}
""",

    "Program9_GeospatialSearch/src/com/demo/geo/model/Location.java": """package com.demo.geo.model;

public class Location {
    private String name;
    private double latitude;
    private double longitude;
    private double distanceKm; // Calculated distance from the user

    public Location(String name, double latitude, double longitude) {
        this.name = name;
        this.latitude = latitude;
        this.longitude = longitude;
    }

    public void setDistanceKm(double distanceKm) {
        this.distanceKm = distanceKm;
    }

    @Override
    public String toString() {
        if (distanceKm > 0) {
            return String.format("%-25s | %.2f km away (Lat: %.4f, Lon: %.4f)", name, distanceKm, latitude, longitude);
        }
        return String.format("%-25s | (Lat: %.4f, Lon: %.4f)", name, latitude, longitude);
    }
}
""",

    "Program9_GeospatialSearch/src/com/demo/geo/dao/LocationDAO.java": """package com.demo.geo.dao;

import com.demo.geo.model.Location;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class LocationDAO {

    public void clearAndInsertSeedData(Connection conn) throws SQLException {
        conn.createStatement().execute("TRUNCATE TABLE locations");

        String sql = "INSERT INTO locations (name, latitude, longitude) VALUES (?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            // Seed data (Let's use Hyderabad landmarks and surrounding areas)
            Object[][] places = {
                {"Charminar", 17.3616, 78.4747},
                {"Golconda Fort", 17.3833, 78.4011},
                {"Hussain Sagar Lake", 17.4239, 78.4738},
                {"Salar Jung Museum", 17.3713, 78.4804},
                {"Ramoji Film City", 17.2543, 78.6808},
                {"Inorbit Mall Cyberabad", 17.4338, 78.3868},
                {"RGIA Airport", 17.2403, 78.4294},
                {"IKEA Hyderabad", 17.4398, 78.3753}
            };

            for (Object[] place : places) {
                pstmt.setString(1, (String) place[0]);
                pstmt.setDouble(2, (Double) place[1]);
                pstmt.setDouble(3, (Double) place[2]);
                pstmt.addBatch();
            }
            pstmt.executeBatch();
            System.out.println("Seeded database with " + places.length + " locations.\\n");
        }
    }

    /**
     * Executes the Haversine formula directly in MySQL to find places within a radius.
     */
    public List<Location> findNearbyLocations(Connection conn, double userLat, double userLon, double radiusKm) throws SQLException {
        List<Location> nearbyPlaces = new ArrayList<>();

        // The Haversine Formula in SQL
        // 6371 is the Earth's radius in kilometers
        String sql = 
            "SELECT name, latitude, longitude, " +
            "( 6371 * acos( cos( radians(?) ) * cos( radians( latitude ) ) " +
            "* cos( radians( longitude ) - radians(?) ) + sin( radians(?) ) " +
            "* sin( radians( latitude ) ) ) ) AS distance " +
            "FROM locations " +
            "HAVING distance <= ? " +
            "ORDER BY distance ASC";

        try (PreparedStatement pstmt = conn.prepareStatement(sql)) {
            pstmt.setDouble(1, userLat); // First part of formula
            pstmt.setDouble(2, userLon); // Longitude offset
            pstmt.setDouble(3, userLat); // Sin offset
            pstmt.setDouble(4, radiusKm); // The HAVING clause filter

            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    Location loc = new Location(
                        rs.getString("name"),
                        rs.getDouble("latitude"),
                        rs.getDouble("longitude")
                    );
                    loc.setDistanceKm(rs.getDouble("distance"));
                    nearbyPlaces.add(loc);
                }
            }
        }
        return nearbyPlaces;
    }
}
""",

    "Program9_GeospatialSearch/src/com/demo/geo/service/GeoService.java": """package com.demo.geo.service;

import com.demo.geo.dao.LocationDAO;
import com.demo.geo.db.DatabaseConnection;
import com.demo.geo.model.Location;
import java.sql.Connection;
import java.util.List;

public class GeoService {
    private LocationDAO locationDAO = new LocationDAO();

    public void runGeospatialDemo() {
        try (Connection conn = DatabaseConnection.getConnection()) {
            
            // 1. Prepare Database
            locationDAO.clearAndInsertSeedData(conn);

            // 2. Simulate User Location
            // Let's pretend the user is standing in HITEC City
            double userLat = 17.4474;
            double userLon = 78.3762;
            double radius = 10.0; // Searching within 10 kilometers

            System.out.println("USER LOCATION: HITEC City (Lat: " + userLat + ", Lon: " + userLon + ")");
            System.out.println("SEARCH RADIUS: " + radius + " km\\n");

            // 3. Execute Database Geospatial Query
            System.out.println("Executing Haversine Formula Query in MySQL...");
            List<Location> results = locationDAO.findNearbyLocations(conn, userLat, userLon, radius);

            // 4. Display Results
            System.out.println("\\n--- Results (Sorted by Distance) ---");
            if (results.isEmpty()) {
                System.out.println("No locations found within that radius.");
            } else {
                for (Location loc : results) {
                    System.out.println(loc.toString());
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
""",

    "Program9_GeospatialSearch/src/com/demo/geo/main/GeoMain.java": """package com.demo.geo.main;

import com.demo.geo.service.GeoService;

public class GeoMain {
    public static void main(String[] args) {
        System.out.println("=== Location-Based Search Engine (Haversine Formula) ===");
        GeoService service = new GeoService();
        service.runGeospatialDemo();
    }
}
"""
}

for rel_path, content in files.items():
    full_path = os.path.join(base_dir, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w") as f:
        f.write(content)

print("Program 9 generated successfully!")
