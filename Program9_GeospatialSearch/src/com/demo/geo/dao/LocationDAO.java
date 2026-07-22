package com.demo.geo.dao;

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
            System.out.println("Seeded database with " + places.length + " locations.\n");
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
