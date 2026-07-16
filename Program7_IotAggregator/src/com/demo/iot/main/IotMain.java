package com.demo.iot.main;

import com.demo.iot.service.IotService;

public class IotMain {
    public static void main(String[] args) {
        System.out.println("=== IoT Data Aggregator Pipeline ===");
        IotService service = new IotService();
        service.simulateAndAggregate();
    }
}
