# Database Programs Explanation Guide

This guide provides a high-level overview of Programs 5 and 6, designed to help you explain the architectural decisions, purpose, and technical concepts demonstrated in each project to your manager. Both programs strictly use **Core Java** and a **MySQL** database, adhering to standard Model-View-Controller (MVC) and Data Access Object (DAO) design patterns.

---

## Program 5: API Response Caching System
**(Located in `Program5_ApiCache/`)**

### Purpose
The goal of this program is to optimize application performance and reduce unnecessary network traffic by utilizing the database as a temporary caching layer for external API requests. Instead of repeatedly querying an external service, the application stores the response in the database for 5 minutes.

### How It Works (L1 / L2 Cache Architecture)
To optimize performance and database load, this program implements a modern **Multi-Level Cache**:
1. **L1 (In-Memory RAM):** Uses the `Caffeine` library to cache data directly in the Java application's RAM. It is checked first. If data is found (a Cache Hit), it is returned instantly (~0.1ms).
2. **L2 (MySQL Database):** If the data is missing from L1 (e.g., after a server restart), the system queries the `api_cache` MySQL table. If a valid record exists, it is promoted back to the L1 cache and returned (~2-5ms).
3. **L3 (Network Fallback):** If the cache is expired or completely missing, it makes an HTTP GET request to the external API, retrieves the JSON payload, and updates both the L2 database and the L1 RAM cache.

### Key Concepts Demonstrated to Highlight:
* **Multi-Level Caching:** Demonstrates an enterprise understanding of protecting the database from unnecessary read queries by placing an ultra-fast Caffeine RAM cache in front of it.
* **"Upsert" Logic:** Demonstrates advanced SQL via the `ON DUPLICATE KEY UPDATE` clause, which elegantly handles inserting a new cache record or updating an existing one without throwing duplicate primary key errors.
* **Time-Based Data Expiration:** Implements sophisticated eviction policies, using `expireAfterWrite` in Caffeine and UNIX timestamp comparisons in MySQL to enforce strict data freshness.

---

## Program 6: JSON Payload to Relational Database Converter
**(Located in `Program6_JsonRelational/`)**

### Purpose
The goal of this program is to demonstrate **data normalization**. It takes a complex, nested data structure (a JSON array containing users and their multiple hobbies) and intelligently parses, flattens, and distributes that data across multiple relational SQL tables.

### How It Works
1. **Jackson JSON Parsing:** Because you have access to external libraries like Jackson, the application uses `com.fasterxml.jackson.databind.ObjectMapper` to effortlessly deserialize the strict JSON payload into a list of strongly-typed `User` objects.
2. **Flattening:** It maps the single JSON object into two separate SQL tables: `users` (Main entity) and `user_hobbies` (A Many-to-One relational mapping).
3. **Reconstruction:** After saving the data, it utilizes an `SQL JOIN` query to stitch the flattened data back together and display it to the console.

### Key Concepts Demonstrated to Highlight:
* **Database Normalization (1NF):** Showcases how to eliminate repeating groups by splitting arrays (hobbies) into a separate linked table with a `FOREIGN KEY`.
* **ACID Transactions:** This is a major talking point. The `JsonService` performs multiple database inserts (one user, multiple hobbies). The program deliberately manages `conn.setAutoCommit(false)` and `conn.commit()`. If any error occurs while inserting hobbies, `conn.rollback()` is triggered, ensuring the database is never left in a partially updated, corrupted state.
* **Relational `JOIN` Queries:** Proves competency in retrieving and combining data across multiple normalized tables simultaneously. 
* **Data Deserialization:** Effectively maps external JSON strings to internal Domain Objects (POJOs) using industry-standard libraries (Jackson) via `TypeReference`.
