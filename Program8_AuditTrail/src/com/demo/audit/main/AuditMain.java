package com.demo.audit.main;

import com.demo.audit.service.AuditService;

public class AuditMain {
    public static void main(String[] args) {
        System.out.println("=== Document Version Control & Audit Trail ===");
        AuditService service = new AuditService();
        service.runAuditDemo();
    }
}
