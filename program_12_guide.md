# Program 12 — API Rate Limiter (Sliding Window)

A complete breakdown of Program 12 covering overview, flow, internals, real-world applications, edge cases, alternatives, learnings, and manager Q&A.

---

## Overview

Program 12 implements a **database-backed API Rate Limiter** using the **Sliding Window Counter** algorithm. In the real world, every public API (Google Maps, Stripe, Twitter/X) must protect itself from abuse — whether it's a malicious bot hammering the server or a buggy client stuck in an infinite loop. This program demonstrates how to enforce a rule like *"User X can only make 5 requests per minute"* using MySQL as the source of truth.

### What Makes This Program Different
This is the first program that uses a **`config.properties`** file. Instead of hardcoding database credentials and business rules directly in Java code, all configurable values are externalized:
```properties
db.url=jdbc:mysql://localhost:3306/demo_ratelimiter
db.user=root
db.password=root
ratelimit.max.requests=5
ratelimit.window.seconds=60
ratelimit.cleanup.older.than.minutes=10
```
This means an operations team can change the rate limit from 5 to 100, or change the database password, **without touching or recompiling a single line of Java code**.

---

## How It Works — The Complete Flow

### Step 1: Configuration Loading
When `RateLimitMain.java` starts, the very first thing it does is call `ConfigLoader.load()`. This reads the `config.properties` file from the project root directory using `java.util.Properties` and `FileInputStream`. If the file is missing, the application throws a `RuntimeException` and refuses to start — this is a deliberate **fail-fast** design. It's better to crash immediately with a clear error than to silently use wrong default values.

### Step 2: The Rate Check (`RateLimitService.checkAndLog()`)
Every time a user makes an API request, the service performs this sequence inside a **database transaction**:

1. **COUNT:** It runs a SQL query to count how many requests this specific user has made to this specific endpoint in the last N seconds (the "sliding window"):
   ```sql
   SELECT COUNT(*) FROM rate_limit_log
   WHERE user_id = ? AND endpoint = ?
   AND requested_at >= NOW(3) - INTERVAL ? SECOND
   ```

2. **DECIDE:** If `count >= maxRequests`, the request is **BLOCKED** (HTTP 429). The transaction is rolled back (no log entry is created for blocked requests).

3. **LOG:** If `count < maxRequests`, the request is **ALLOWED**. A new row is inserted into `rate_limit_log` with the current timestamp, and the transaction is committed.

### Step 3: The Sliding Window in Action
The "sliding window" is not a fixed clock interval (like "every minute starting at :00"). It is a **rolling** 60-second period that moves forward continuously. For example:
- At `14:00:30`, the window looks back to `13:59:30`
- At `14:00:35`, the window looks back to `13:59:35`
- A request logged at `13:59:31` is inside the window at `14:00:30` but **outside** the window at `14:00:32`

This is far more accurate than a fixed window, which can allow burst attacks at the boundary (e.g., 5 requests at `13:59:59` and 5 more at `14:00:01`).

### Step 4: Per-User, Per-Endpoint Isolation
The rate limit is scoped to the combination of `(user_id, endpoint)`. This means:
- `user_aviral` hitting `/api/v1/data` 5 times does NOT affect `user_bob` hitting the same endpoint.
- `user_aviral` hitting `/api/v1/data` 5 times does NOT affect `user_aviral` hitting `/api/v1/reports`.

Each combination gets its own independent counter.

### Step 5: Cleanup (Housekeeping)
The `rate_limit_log` table would grow infinitely if we never cleaned it. The `cleanup()` method runs:
```sql
DELETE FROM rate_limit_log WHERE requested_at < NOW() - INTERVAL ? MINUTE
```
This removes entries older than the configured threshold (default: 10 minutes). In production, this would be a scheduled cron job or a background thread.

### Step 6: Fail-Open Policy
If the MySQL database itself crashes or times out, the `catch` block returns `allowed = true`. This is called a **fail-open** policy — we'd rather let a few extra requests through than block all legitimate users just because the rate limiter's database is temporarily down.

---

## The Database Schema

```sql
CREATE TABLE rate_limit_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    endpoint VARCHAR(255) NOT NULL,
    requested_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_user_endpoint_time (user_id, endpoint, requested_at)
);
```

### Why `TIMESTAMP(3)`?
Standard `TIMESTAMP` has 1-second precision. If a user sends 3 requests in the same second, they'd all get the same timestamp and the `COUNT` could be inaccurate. `TIMESTAMP(3)` stores milliseconds, giving us sub-second precision.

### Why the Composite Index?
The `INDEX idx_user_endpoint_time (user_id, endpoint, requested_at)` is critical for performance. Without it, every rate check would do a full table scan across millions of rows. With the index, MySQL can jump directly to the exact user + endpoint + time range in microseconds. This is called a **covering index** because it covers all three columns used in the `WHERE` clause.

---

## Real-World Use Cases

1. **Public APIs (Google Maps, Stripe):** Free-tier users get 100 requests/day. Paid users get 10,000. The rate limiter enforces these tiers.
2. **Login Brute-Force Protection:** Limit login attempts to 5 per minute per IP address. After 5 failed attempts, block the IP temporarily.
3. **E-commerce Anti-Bot:** During flash sales, bots try to buy inventory faster than humans. Rate limiting ensures each user can only click "Buy" once per second.
4. **Microservices Circuit Breaker:** If Service A calls Service B too aggressively, Service B's rate limiter protects it from being overwhelmed.
5. **SMS/Email APIs (Twilio, SendGrid):** Prevent accidental infinite loops from sending thousands of SMS messages and running up a massive bill.

---

## Edge Cases & How We Handle Them

| Edge Case | How We Handle It |
|---|---|
| Database is down | **Fail-open:** Allow the request rather than blocking all users |
| `config.properties` is missing | **Fail-fast:** Crash immediately with a clear error message |
| Two requests arrive at the exact same millisecond | `TIMESTAMP(3)` provides millisecond precision; transaction isolation prevents double-counting |
| Table grows infinitely | `cleanup()` method deletes entries older than the configured threshold |
| A required config key is missing | `ConfigLoader.get()` throws a `RuntimeException` with the missing key name |
| User sends request to a brand new endpoint | Works automatically — `COUNT` returns 0 for any new (user, endpoint) combination |

---

## Alternative Approaches

| Approach | Pros | Cons |
|---|---|---|
| **Database Sliding Window (Our Approach)** | Persistent, survives restarts, auditable | Slower than in-memory, DB dependency |
| **In-Memory (ConcurrentHashMap)** | Extremely fast (~0.01ms) | Lost on restart, not shared across servers |
| **Redis (`INCR` + `EXPIRE`)** | Fast, shared across servers, built-in TTL | Requires Redis infrastructure |
| **Token Bucket Algorithm** | Allows controlled bursts | More complex to implement |
| **Leaky Bucket Algorithm** | Smooth, constant output rate | Can delay legitimate requests |

---

## What We Learned

1. **Externalized Configuration:** How to use `java.util.Properties` and `FileInputStream` to read settings from a `config.properties` file, eliminating all hardcoded values.
2. **Fail-Fast vs Fail-Open:** The application crashes immediately if config is missing (fail-fast), but allows requests if the DB is down (fail-open). These are deliberate, opposite design choices for different failure scenarios.
3. **Sliding Window Algorithm:** A time-based counting technique that is far more accurate than fixed windows for rate limiting.
4. **Composite Indexes:** How a multi-column database index dramatically speeds up queries that filter on multiple columns simultaneously.
5. **Millisecond Timestamps:** `TIMESTAMP(3)` provides sub-second precision, critical for high-throughput systems where multiple events can occur within the same second.
6. **Transaction Isolation:** Wrapping the COUNT + INSERT in a single transaction prevents race conditions where two simultaneous requests could both "see" 4/5 and both get allowed, pushing the count to 6.
7. **Data Hygiene:** Old, irrelevant data must be periodically purged to keep table sizes manageable and query performance fast.

---

## Manager / Senior Dev Q&A

### Q1: Why use a database for rate limiting instead of just doing it in memory?
**A:** In-memory rate limiting (like a `ConcurrentHashMap`) is faster, but it has two critical flaws: (1) The data is lost when the server restarts, resetting all rate limits. (2) If you run multiple instances of the application behind a load balancer, each instance has its own separate counter, so a user could make 5 requests to Server A and 5 more to Server B, bypassing the limit entirely. A shared database acts as a single source of truth across all instances.

### Q2: What is the difference between a "sliding window" and a "fixed window"?
**A:** A fixed window resets at hard boundaries (e.g., every minute at :00). This creates a vulnerability: a user can make 5 requests at 13:59:59 and 5 more at 14:00:01 — that's 10 requests in 2 seconds. A sliding window always looks back exactly 60 seconds from *right now*, so the 5 requests at 13:59:59 are still counted at 14:00:01. It eliminates the boundary burst problem.

### Q3: Why do you use `TIMESTAMP(3)` instead of regular `TIMESTAMP`?
**A:** Regular `TIMESTAMP` has 1-second granularity. In a high-traffic system, hundreds of requests can arrive within the same second. If two requests have the same timestamp, the `COUNT` query might undercount. `TIMESTAMP(3)` adds millisecond precision, reducing the chance of collisions by 1000x.

### Q4: What does "fail-open" mean and why did you choose it?
**A:** "Fail-open" means that when the rate limiter itself fails (e.g., DB timeout), we allow the request through instead of blocking it. The alternative is "fail-closed" (block everything). We chose fail-open because blocking all legitimate users due to a database hiccup causes more business damage than temporarily allowing a few extra requests. However, for security-critical systems (like login brute-force protection), you would choose fail-closed.

### Q5: Why is there a composite index on `(user_id, endpoint, requested_at)`?
**A:** Our `COUNT` query filters on all three columns: `WHERE user_id = ? AND endpoint = ? AND requested_at >= ?`. Without the index, MySQL would scan every single row in the table to find matches. With the composite index, MySQL can use a B-tree to jump directly to the matching user, then the matching endpoint, then scan only the rows within the time range. On a table with 10 million rows, this is the difference between 5 seconds and 5 milliseconds.

### Q6: How would you make this production-ready?
**A:** Four improvements:
1. **Connection Pooling:** Replace `DriverManager.getConnection()` with HikariCP to reuse database connections instead of opening a new one per request.
2. **Scheduled Cleanup:** Run the `cleanup()` method as a `ScheduledExecutorService` background thread instead of manually calling it.
3. **Redis Migration:** For sub-millisecond performance at massive scale, migrate from MySQL to Redis using `INCR` + `EXPIRE` commands.
4. **Response Headers:** Return `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers to tell the client how many requests they have left and when the window resets.

### Q7: Why is the rate limit scoped per user AND per endpoint?
**A:** Different API endpoints have different costs. A lightweight `GET /api/status` endpoint can handle 1000 requests/minute, but a heavy `POST /api/generate-report` endpoint that triggers complex database queries should be limited to 10/minute. Scoping per endpoint allows fine-grained control. Additionally, one user's activity should never affect another user's quota.

### Q8: Why did you use `config.properties` instead of hardcoding?
**A:** Hardcoding violates the **Twelve-Factor App** methodology (a widely accepted set of best practices). Configuration changes (like adjusting the rate limit from 5 to 50 during a traffic spike) should not require code changes, code reviews, recompilation, or redeployment. With a properties file, the ops team can simply edit the file and restart the application. In even more advanced setups, tools like Spring Cloud Config or Consul allow configuration changes without even restarting.
