package com.demo.geo.service;

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
            System.out.println("SEARCH RADIUS: " + radius + " km\n");

            // 3. Execute Database Geospatial Query
            System.out.println("Executing Haversine Formula Query in MySQL...");
            List<Location> results = locationDAO.findNearbyLocations(conn, userLat, userLon, radius);

            // 4. Display Results
            System.out.println("\n--- Results (Sorted by Distance) ---");
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
