package com.demo.ratelimit.main;

import com.demo.ratelimit.model.RateLimitResult;
import com.demo.ratelimit.service.RateLimitService;
import com.demo.ratelimit.util.ConfigLoader;

public class RateLimitMain {
    public static void main(String[] args) {
        System.out.println("=== API Rate Limiter (Sliding Window) ===\n");

        // Load configuration from config.properties
        ConfigLoader.load();

        RateLimitService service = new RateLimitService();
        service.clearData();

        String userId = "user_aviral";
        String endpoint = "/api/v1/data";

        // Simulate 8 rapid API calls from the same user
        System.out.println("\n[Scenario 1] User '" + userId + "' makes 8 rapid requests to '" + endpoint + "':");
        System.out.println("(Limit is 5 requests per 60 seconds)\n");

        for (int i = 1; i <= 8; i++) {
            RateLimitResult result = service.checkAndLog(userId, endpoint);
            System.out.println("  Request #" + i + ": " + result);
        }

        // A different user should NOT be affected by user_aviral's rate limit
        System.out.println("\n[Scenario 2] A different user makes a request to the same endpoint:");
        String otherUser = "user_bob";
        RateLimitResult bobResult = service.checkAndLog(otherUser, endpoint);
        System.out.println("  " + otherUser + ": " + bobResult);

        // Same user, different endpoint should also work independently
        System.out.println("\n[Scenario 3] Same user '" + userId + "' hits a DIFFERENT endpoint:");
        String otherEndpoint = "/api/v1/reports";
        RateLimitResult otherEndpointResult = service.checkAndLog(userId, otherEndpoint);
        System.out.println("  " + otherEndpoint + ": " + otherEndpointResult);

        // Cleanup
        System.out.println("\n[Housekeeping] Running cleanup job...");
        service.cleanup();
    }
}
