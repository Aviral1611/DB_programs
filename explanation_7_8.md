# Database Programs Explanation Guide (Programs 7 & 8)

This guide provides a high-level overview of Programs 7 and 8, designed to help you explain the architectural decisions and technical concepts to your manager. Both programs use **Core Java** and a **MySQL** database, adhering to standard MVC and DAO design patterns.

---

## Program 7: IoT Sensor Data Aggregator (Batch Processing)
**(Located in `Program7_IotAggregator/`)**

### Purpose
The goal of this program is to demonstrate how to offload heavy data calculations to the database engine rather than trying to process millions of rows in Java memory. This simulates an IoT environment (like temperature sensors or web logs) where raw data is constantly streaming in, and the system periodically aggregates it into manageable summaries (averages, maximums, minimums).

### How It Works
1. **Data Ingestion:** The `IotService` simulates 100 raw data readings across multiple sensors spanning a 2-hour window, pushing them into the `raw_sensor_data` table.
2. **Batch Aggregation:** Instead of querying all 100 rows into Java and doing math manually, the `SensorDAO` runs a single, highly optimized SQL query using `GROUP BY`, `AVG()`, `MAX()`, and `MIN()`. 
3. **Upserting Metrics:** The aggregated results are then pushed directly into an `hourly_aggregates` table in bulk.

### Key Concepts Demonstrated to Highlight:
* **Database-Side Aggregation:** Proves an understanding that the SQL engine is much faster at crunching numbers (`GROUP BY`) than pulling data into the application layer.
* **Batch Processing:** Simulates a real-world cron job or background process that rolls up noisy raw data into clean, reportable metrics.
* **Advanced `ON DUPLICATE KEY UPDATE`:** If the aggregation job runs twice for the same hour, it neatly updates the existing metric row rather than failing or duplicating data.

---

## Program 8: Document Version Control & Audit Trail
**(Located in `Program8_AuditTrail/`)**

### Purpose
The goal of this program is to demonstrate an **Enterprise Audit Trail**. In many corporate and banking applications, you cannot simply update a database row and lose the old data. You must maintain a strict history of *who* changed it, *what* the old data was, and *when* it was changed.

### How It Works
1. **Creation:** A user (e.g., Alice) creates a draft document in the `documents` table.
2. **Editing:** When someone else (e.g., Bob) edits the document, the application first locks the specific row. It copies the old title and content, and inserts it into a `document_history` table.
3. **Updating:** Only after the history is safely saved does it overwrite the live document with the new data.
4. **Retrieval:** The program queries both tables to print out the current "Live" version, followed by a chronological history trail of every change ever made.

### Key Concepts Demonstrated to Highlight:
* **Row Locking (`FOR UPDATE`):** This is a massive talking point for concurrency. When Bob starts editing the document, the SQL query `SELECT ... FOR UPDATE` explicitly locks that row. If Charlie tries to edit it at the exact same millisecond, Charlie's query is forced to wait. This prevents race conditions.
* **ACID Transactions:** The process of "saving history" and "updating live document" is wrapped in a strict transaction (`conn.setAutoCommit(false)`). If the database crashes right between step 2 and 3, it automatically rolls back, guaranteeing the audit trail is never corrupted or out of sync with the live data.
* **Foreign Key Constraints (`ON DELETE CASCADE`):** If the live document is deleted, the database automatically cleans up the corresponding history logs to prevent orphaned data.
