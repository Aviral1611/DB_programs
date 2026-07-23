# Database Programs Explanation Guide (Programs 10 & 11)

This guide provides a detailed, in-depth breakdown of Programs 10 and 11 — covering the architecture, the flow, and the key concepts you can confidently explain to your manager.

---

## Program 10: URL Shortener Service (Base62 Encoding)
**(Located in `Program10_UrlShortener/`)**

### Purpose
This program replicates the core engine behind services like **bit.ly** or **tinyurl.com**. It takes a massive, ugly URL and converts it into a short, shareable 6-character code. It also tracks how many times each short link has been clicked, providing basic click analytics.

### The Complete Flow

#### Step 1: Shortening a URL (`UrlService.shortenUrl()`)
When a user submits a long URL, the following happens:

1. **Code Generation:** The `UrlService` generates a random 6-character string using a character set called **Base62** (`0-9`, `a-z`, `A-Z`). This gives us 62^6 = **56.8 billion** possible unique codes. It uses `java.security.SecureRandom` instead of `java.util.Random` because `SecureRandom` is cryptographically strong and produces truly unpredictable codes, preventing attackers from guessing the next short URL.

2. **Collision Detection:** Before saving, the service calls `urlDAO.shortCodeExists()` to check if the randomly generated code already exists in the database. If it does (a "collision"), it regenerates a new code and retries up to 5 times. This is critical because if two different long URLs accidentally got the same short code, one would overwrite the other.

3. **Database Insert:** Once a unique code is confirmed, the `UrlDAO` inserts a new row into `short_urls` with the code, the original URL, and a `click_count` initialized to `0`.

#### Step 2: Clicking a Short URL (`UrlService.resolveUrl()`)
When a user "clicks" a short link, the system needs to do two things atomically:

1. **Increment the Counter:** The DAO runs `UPDATE short_urls SET click_count = click_count + 1 WHERE short_code = ?`. This is an **atomic SQL operation** — it means that even if 1000 users click the same link at the exact same millisecond, the database engine guarantees every single click is counted accurately without race conditions. The `click_count + 1` happens inside the database engine itself, not in Java.

2. **Return the Original URL:** After incrementing, it fetches the `original_url` so the application can redirect the user to the correct destination.

#### Step 3: Analytics (`UrlService.displayAnalytics()`)
The DAO queries all short URLs sorted by `click_count DESC`, giving a leaderboard of the most popular links.

### Key Concepts Demonstrated:
* **Base62 Encoding:** Industry-standard technique used by real URL shorteners. It is URL-safe (no special characters like `+` or `/`).
* **Collision Detection:** Shows awareness of probabilistic uniqueness and the importance of checking before inserting.
* **Atomic Counter Increment:** The SQL `click_count = click_count + 1` pattern is thread-safe and used heavily in analytics systems.
* **`SecureRandom` vs `Random`:** Demonstrates security-conscious coding practices.
* **Proper Exception Handling:** Every database and service method has specific `try-catch` blocks with meaningful error messages.

---

## Program 11: Secure Password Vault (AES-128 Encryption at Rest)
**(Located in `Program11_PasswordVault/`)**

### Purpose
This program demonstrates the security principle of **"Encryption at Rest"**. It simulates a password manager (like LastPass or 1Password). Passwords are encrypted in the Java application layer *before* they are ever sent to the database. If a hacker gains access to the MySQL database, all they see is unreadable Base64 gibberish — the actual passwords are mathematically impossible to recover without the secret key.

### The Complete Flow

#### Step 1: Storing a Password (`VaultService.storeCredential()`)
When a user saves a new credential (e.g., Gmail / `MyGmail@2026!`):

1. **Encryption (Java Layer):** The `VaultService` calls `AESEncryptor.encrypt("MyGmail@2026!")`. Inside this utility:
   - It initializes a `javax.crypto.Cipher` instance with the **AES algorithm**.
   - It uses a 16-byte (128-bit) secret key to transform the plaintext into raw encrypted bytes.
   - It then encodes those raw bytes into a **Base64 string** (e.g., `K7xZ2mP...`). Base64 encoding is necessary because raw encrypted bytes contain non-printable characters that would corrupt a `VARCHAR` database column.
   
2. **Database Storage:** The `VaultDAO` receives the Base64-encoded ciphertext and stores it in the `encrypted_password` column. The plaintext password **never** touches the database.

#### Step 2: The Hacker's View (`VaultService.displayDatabaseView()`)
This step simulates what would happen if someone broke into your MySQL server and ran `SELECT * FROM credentials`. They would see:
```
Service: Gmail          | User: aviral.bansal   | Encrypted: K7xZ2mP9q...
Service: GitHub         | User: aviral-dev      | Encrypted: 8nRtW1xYb...
```
The passwords are completely unreadable. Without the secret key that lives inside the Java application, the data is useless.

#### Step 3: Retrieving a Password (`VaultService.retrieveCredential()`)
When the legitimate user wants to see their Gmail password:

1. **Database Fetch:** The `VaultDAO` queries the `credentials` table and returns the encrypted Base64 string.
2. **Decryption (Java Layer):** The `VaultService` calls `AESEncryptor.decrypt(cipherText)`:
   - It decodes the Base64 string back into raw encrypted bytes.
   - It initializes the `Cipher` in `DECRYPT_MODE` with the same secret key.
   - It reverses the AES transformation, producing the original plaintext: `MyGmail@2026!`.

#### Step 4: Error Handling
The program also demonstrates what happens when you try to retrieve a credential that doesn't exist. Instead of crashing with a `NullPointerException`, the service layer gracefully prints `[NOT FOUND]` and continues running.

### Key Concepts Demonstrated:
* **AES-128 Encryption:** Industry-standard symmetric encryption algorithm used by governments and banks worldwide.
* **Encryption at Rest:** The principle that sensitive data must be encrypted *before* it is written to disk (the database), not after.
* **Base64 Encoding:** Necessary to safely store binary encrypted bytes in a text-based SQL column without data corruption.
* **Separation of Concerns:** The encryption/decryption logic lives in a dedicated `AESEncryptor` utility class, completely isolated from the DAO and database logic. The DAO never knows or cares that the data is encrypted.
* **`ON DUPLICATE KEY UPDATE`:** If the user updates their Gmail password, the system gracefully overwrites the old encrypted value instead of throwing a duplicate key error.
* **Security Best Practice Note:** The code includes explicit comments warning that the hardcoded key is for demo purposes only, and in production, keys must come from environment variables or a secrets manager (like AWS KMS or HashiCorp Vault).
