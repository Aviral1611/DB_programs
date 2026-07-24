package com.demo.audit.main;

import com.demo.audit.service.AuditService;
import com.demo.audit.util.ConfigLoader;

public class AuditMain {
    public static void main(String[] args) {
        System.out.println("=== Document Version Control & Audit Trail ===\n");

        // Load configuration from config.properties
        ConfigLoader.load();

        AuditService service = new AuditService();
        service.runAuditDemo();
    }
}
