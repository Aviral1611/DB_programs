package com.demo.ratelimit.model;

/**
 * Immutable result object returned after a rate limit check.
 * Contains whether the request is allowed and diagnostic metadata.
 */
public class RateLimitResult {
    private final boolean allowed;
    private final int currentCount;
    private final int maxAllowed;
    private final int windowSeconds;

    public RateLimitResult(boolean allowed, int currentCount, int maxAllowed, int windowSeconds) {
        this.allowed = allowed;
        this.currentCount = currentCount;
        this.maxAllowed = maxAllowed;
        this.windowSeconds = windowSeconds;
    }

    public boolean isAllowed() { return allowed; }
    public int getCurrentCount() { return currentCount; }
    public int getMaxAllowed() { return maxAllowed; }
    public int getWindowSeconds() { return windowSeconds; }

    @Override
    public String toString() {
        if (allowed) {
            return String.format("[200 OK] Request ALLOWED (%d/%d used in last %ds)", currentCount, maxAllowed, windowSeconds);
        } else {
            return String.format("[429 TOO MANY REQUESTS] BLOCKED! (%d/%d used in last %ds)", currentCount, maxAllowed, windowSeconds);
        }
    }
}
