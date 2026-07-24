# Program 13 — Gaming Leaderboard (Window Functions)

A complete breakdown of Program 13 covering overview, flow, internals, real-world applications, edge cases, alternatives, learnings, and manager Q&A.

---

## Overview

Program 13 implements a **real-time gaming leaderboard** that dynamically ranks players based on their best scores. The key innovation here is that rankings are not stored in the database — they are **computed on the fly** using MySQL **Window Functions** (`RANK()`, `DENSE_RANK()`). This means the leaderboard is always live, always accurate, and never stale.

Every score a player submits is permanently recorded. The system never overwrites old scores — it keeps a full history, allowing players to track their improvement over time and see which attempt was their personal best.

Like Program 12, all configuration (DB credentials, leaderboard size) is externalized in `config.properties`.

---

## How It Works — The Complete Flow

### Step 1: Player Registration
Players are registered in the `players` table with a `UNIQUE` constraint on `username`. If you try to register "ShadowNinja" twice, MySQL will throw a `DuplicateKeyException` — no duplicates allowed.

### Step 2: Score Submission
Every time a player finishes a game round, their score is inserted into the `scores` table. We **never update or delete** old scores. This is an important design decision:
- It creates a complete audit trail of every game played.
- It allows us to calculate personal bests, averages, and improvement trends.
- It prevents accidental data loss (you can't accidentally overwrite a high score).

### Step 3: The Leaderboard Query (The Heart of the Program)
This is where the magic happens. The `LeaderboardDAO.getLeaderboard()` method runs a single, powerful SQL query:

```sql
SELECT 
    p.username,
    MAX(s.score) AS best_score,
    COUNT(s.score_id) AS total_submissions,
    RANK() OVER (ORDER BY MAX(s.score) DESC) AS player_rank,
    DENSE_RANK() OVER (ORDER BY MAX(s.score) DESC) AS player_dense_rank
FROM players p
JOIN scores s ON p.player_id = s.player_id
GROUP BY p.player_id, p.username
ORDER BY best_score DESC
LIMIT ?
```

Let's break this down piece by piece:

#### `MAX(s.score) AS best_score`
A player may have submitted 5 scores: `[720, 850, 940, 800, 610]`. We only care about their **personal best** for the leaderboard. `MAX()` finds `940` instantly without Java having to loop through an array.

#### `COUNT(s.score_id) AS total_submissions`
Tells us how many rounds the player has played. More attempts = more dedicated player.

#### `RANK() OVER (ORDER BY MAX(s.score) DESC)`
This is a **Window Function**. Unlike `GROUP BY` which collapses rows, `RANK()` assigns a ranking number to each row based on the ordering. If two players tie at 940 points, they both get Rank #1. The next player gets Rank **#3** (not #2) — the rank "skips" over the tie.

#### `DENSE_RANK() OVER (ORDER BY MAX(s.score) DESC)`
Works identically to `RANK()`, but it does **not** skip numbers after a tie. If two players tie at Rank #1, the next player gets Rank **#2** (not #3). This is useful when you want to award prizes to "the top 3 ranks" — with `DENSE_RANK`, you guarantee exactly 3 distinct rank numbers exist.

### Step 4: Player History Deep Dive
The `displayPlayerHistory()` method shows all of a player's individual game attempts in chronological order. It uses a **correlated subquery** to dynamically mark which attempt was their personal best:

```sql
CASE WHEN s.score = (SELECT MAX(s2.score) FROM scores s2 WHERE s2.player_id = p.player_id)
    THEN '<-- PERSONAL BEST' ELSE '' END AS marker
```

This subquery runs once per row and compares the current row's score against the player's all-time maximum. If they match, it tags that row with a visual marker.

---

## The Database Schema

```sql
CREATE TABLE players (
    player_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE scores (
    score_id INT AUTO_INCREMENT PRIMARY KEY,
    player_id INT NOT NULL,
    score INT NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(player_id) ON DELETE CASCADE,
    INDEX idx_player_score (player_id, score DESC)
);
```

### Why Separate Tables?
We could have put everything in one table, but that would violate **Database Normalization**. A player's username, registration date, and profile data belong in the `players` table. Their game scores (which can be hundreds of rows) belong in the `scores` table. This 1-to-Many relationship is linked by `player_id`.

### Why `INDEX idx_player_score (player_id, score DESC)`?
When we look up a player's best score, MySQL needs to find all rows for that `player_id` and then find the `MAX(score)`. The composite index lets MySQL jump directly to the player's rows and scan them in descending order — the first row it hits is already the highest score. Without this index, MySQL would scan the entire `scores` table.

### Why `ON DELETE CASCADE`?
If a player account is deleted from the `players` table, all their scores in the `scores` table are automatically cleaned up. No orphaned data.

---

## RANK() vs DENSE_RANK() vs ROW_NUMBER() — The Critical Difference

This is the single most important concept in this program. Here is an example with 5 players:

| Player | Best Score | `RANK()` | `DENSE_RANK()` | `ROW_NUMBER()` |
|---|---|---|---|---|
| CodeWizard | 990 | 1 | 1 | 1 |
| ShadowNinja | 940 | 2 | 2 | 2 |
| PixelQueen | 940 | 2 | 2 | 3 |
| DragonSlayer | 880 | 4 | 3 | 4 |
| StormBreaker | 850 | 5 | 4 | 5 |

- **`RANK()`**: ShadowNinja and PixelQueen tie at #2. DragonSlayer is #4 (skips #3).
- **`DENSE_RANK()`**: ShadowNinja and PixelQueen tie at #2. DragonSlayer is #3 (no gap).
- **`ROW_NUMBER()`**: No ties at all. One of the tied players arbitrarily gets #2, the other gets #3.

**When to use which:**
- `RANK()` — When you want to show competitive standings (like the Olympics: Gold, Gold, no Silver, Bronze).
- `DENSE_RANK()` — When you want to award prizes to "Top N ranks" (guarantees N distinct ranks exist).
- `ROW_NUMBER()` — When you need pagination or strictly unique numbering (like displaying "Page 1: rows 1-10").

---

## Real-World Use Cases

1. **Mobile Gaming (Clash Royale, PUBG):** Real-time global and regional leaderboards updated after every match.
2. **E-Learning Platforms (LeetCode, HackerRank):** Ranking users by problems solved, contest scores, or streaks.
3. **Sales Dashboards:** Ranking sales representatives by quarterly revenue using `RANK()` to identify top performers.
4. **Fitness Apps (Strava):** Ranking runners on a route segment by their fastest time.
5. **E-commerce (Amazon):** Ranking products by sales volume or reviews — "Best Sellers" lists are just leaderboards.

---

## Edge Cases & How We Handle Them

| Edge Case | How We Handle It |
|---|---|
| Two players have the exact same best score | Both `RANK()` and `DENSE_RANK()` correctly assign them the same rank |
| Player registers but never submits a score | They don't appear on the leaderboard (the `JOIN` naturally excludes them) |
| Player submits a negative or zero score | Currently allowed — in production, add a `CHECK (score > 0)` constraint |
| Duplicate username registration | MySQL throws `DuplicateKeyException` due to the `UNIQUE` constraint |
| Player account is deleted | `ON DELETE CASCADE` automatically removes all their scores |
| Millions of scores in the table | The composite `INDEX idx_player_score` keeps `MAX()` queries fast |
| Config file missing | `ConfigLoader` throws `RuntimeException` immediately (fail-fast) |

---

## Alternative Approaches

| Approach | Pros | Cons |
|---|---|---|
| **Window Functions in SQL (Our Approach)** | Always accurate, zero application logic | Requires MySQL 8.0+, computed on every query |
| **Materialized View / Summary Table** | Pre-computed, extremely fast reads | Stale data until refreshed, extra storage |
| **Redis Sorted Sets (`ZADD`, `ZRANK`)** | Sub-millisecond reads, built for leaderboards | Requires Redis infrastructure, data lost on crash |
| **Application-Level Sorting (Java)** | No special SQL needed | Pulls all data into memory, O(n log n) sort, crashes on large datasets |
| **Stored Procedures** | Logic lives in DB, reusable across apps | Harder to debug, version control, and unit test |

---

## What We Learned

1. **Window Functions (`RANK`, `DENSE_RANK`):** How to compute rankings dynamically in SQL without storing rank numbers in the database. The ranking is always live and always correct.
2. **The Difference Between RANK, DENSE_RANK, and ROW_NUMBER:** Three similar-sounding functions with critically different behaviors for handling ties.
3. **Append-Only Data Design:** Instead of updating a single "high score" column, we append every score as a new row. This preserves full history and allows richer analytics (averages, trends, improvement tracking).
4. **Correlated Subqueries:** How a subquery inside a `CASE WHEN` can reference the outer query's data to dynamically tag rows (the "personal best" marker).
5. **Composite Indexes for Aggregation:** An index on `(player_id, score DESC)` dramatically speeds up `MAX(score)` queries because MySQL can find the answer by reading just the first index entry.
6. **Externalized Configuration:** Continued practice of reading all settings from `config.properties` instead of hardcoding.
7. **1-to-Many Relationship Design:** Properly splitting data across `players` and `scores` tables with Foreign Keys and Cascade Deletes.

---

## Manager / Senior Dev Q&A

### Q1: Why are rankings computed dynamically instead of stored in a column?
**A:** If we stored the rank in a column, every time a new score is submitted, we would have to recalculate and update the rank of every single player in the database. With 1 million players, that's 1 million `UPDATE` statements on every score submission. By using `RANK() OVER(...)`, the database computes rankings on the fly only when someone actually views the leaderboard. Writes are cheap (one `INSERT`), reads do the math.

### Q2: What version of MySQL do Window Functions require?
**A:** Window Functions (`RANK()`, `DENSE_RANK()`, `ROW_NUMBER()`, `LAG()`, `LEAD()`, etc.) were introduced in **MySQL 8.0** (released April 2018). They are not available in MySQL 5.7 or earlier. If you're stuck on 5.7, you would have to simulate ranking using user-defined variables (`@rank := @rank + 1`), which is messy and error-prone.

### Q3: Why do you keep all scores instead of just updating the highest?
**A:** Three reasons:
1. **Audit Trail:** We can prove every game was played and every score was legitimate.
2. **Analytics:** We can calculate averages, medians, improvement rates, and streaks — none of which are possible with a single "best score" column.
3. **Data Integrity:** `INSERT` is safer than `UPDATE`. An `UPDATE` could accidentally overwrite a high score with a lower one due to a bug. With append-only inserts, old data is never touched.

### Q4: What is the difference between `RANK()` and `DENSE_RANK()`?
**A:** Both handle ties the same way (tied players get the same rank number). The difference is what happens *after* the tie:
- `RANK()` **skips** numbers: Ranks go 1, 2, 2, **4** (no #3 exists).
- `DENSE_RANK()` **does not skip**: Ranks go 1, 2, 2, **3**.
Use `RANK()` for competitive standings. Use `DENSE_RANK()` when you need to guarantee "Top N" positions (e.g., "prize for top 3 ranks").

### Q5: What is a correlated subquery and why did you use one?
**A:** A correlated subquery is a subquery that references a column from the outer query. In our `displayPlayerHistory()` method, the subquery `(SELECT MAX(s2.score) FROM scores s2 WHERE s2.player_id = p.player_id)` runs once for each row in the outer query. It compares each individual score against the player's all-time best to decide whether to tag it with "PERSONAL BEST". It is more readable than a self-JOIN for this use case.

### Q6: How would you handle a leaderboard with millions of players?
**A:** Three strategies:
1. **Pagination:** Use `LIMIT` and `OFFSET` to only compute rankings for the visible page (Top 10, Top 50).
2. **Materialized Summary Table:** Run a scheduled batch job (like Program 7's aggregation) that pre-computes rankings into a `leaderboard_cache` table every 5 minutes.
3. **Redis Sorted Sets:** Redis has built-in `ZADD` (add score) and `ZRANK` (get rank) commands that operate in O(log N) time, making them ideal for real-time leaderboards with millions of entries.

### Q7: The `GROUP BY` includes both `p.player_id` and `p.username`. Why both?
**A:** MySQL's `ONLY_FULL_GROUP_BY` mode (enabled by default in MySQL 8.0) requires that every non-aggregated column in the `SELECT` clause must appear in the `GROUP BY` clause. Since we `SELECT p.username`, it must be in the `GROUP BY`. We group by `player_id` (the actual primary key) for correctness, and add `username` to satisfy SQL's strict mode. Grouping by just `username` alone would be semantically wrong because usernames could theoretically change.

### Q8: Why use `config.properties` for the leaderboard limit instead of hardcoding `10`?
**A:** Because different contexts need different limits. A mobile app might show Top 5 (small screen). A desktop dashboard might show Top 50. An admin panel might show Top 1000. By externalizing the limit, the same compiled Java code can serve all three use cases — just change the config file and restart.
