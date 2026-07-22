package com.demo.geo.main;

import com.demo.geo.service.GeoService;

public class GeoMain {
    public static void main(String[] args) {
        System.out.println("=== Location-Based Search Engine (Haversine Formula) ===");
        GeoService service = new GeoService();
        service.runGeospatialDemo();
    }
}
