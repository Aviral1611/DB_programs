package com.demo.geo.model;

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
