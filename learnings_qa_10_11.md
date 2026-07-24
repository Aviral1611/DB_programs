# Programs 10 & 11 — Learnings & Senior Dev Q&A

This document summarizes the key takeaways from both programs and prepares you for the kind of questions a senior developer or tech lead would ask during a code review or walkthrough.

---

## What We Learned

### From Program 10 (URL Shortener)
1. **Base62 Encoding** — How to generate short, URL-safe codes using only alphanumeric characters (`0-9`, `a-z`, `A-Z`), giving 56.8 billion possible combinations with just 6 characters.
2. **Collision Detection** — When generating random values, there is always a chance of duplicates. We learned to check the database first and retry with a limit, rather than blindly inserting and crashing.
3. **`SecureRandom` vs `Random`** — `java.util.Random` is predictable (an attacker can guess the next value). `SecureRandom` is cryptographically strong and should always be used when generating tokens, codes, or anything security-sensitive.
4. **Atomic SQL Operations** — The pattern `SET click_count = click_count + 1` is thread-safe because the increment happens inside the database engine. If we fetched the count into Java, added 1, and wrote it back, two simultaneous clicks could overwrite each other (a race condition).
5. **Analytics from Raw Data** — How to use `ORDER BY click_count DESC` to build simple but effective reporting dashboards directly from operational data.

### From Program 11 (Password Vault)
1. **Encryption at Rest** — Sensitive data must be encrypted *before* it is stored in the database, not after. If the database is breached, the data is useless without the key.
2. **AES Symmetric Encryption** — How `javax.crypto.Cipher` works: the same key encrypts and decrypts the data. AES-128 uses a 16-byte key and is considered unbreakable by modern computers.
3. **Base64 Encoding** — Raw encrypted bytes contain non-printable characters (like null bytes) that would corrupt a `VARCHAR` column. Base64 converts them into safe, printable ASCII characters for storage.
4. **Separation of Concerns** — The `AESEncryptor` utility is completely isolated from the DAO. The DAO has no idea the data is encrypted. This means we could swap AES for a different algorithm without touching a single line of database code.
5. **Key Management Awareness** — Even though we hardcoded the key for the demo, we learned that in production, keys must live in environment variables, AWS KMS, or HashiCorp Vault — never in source code.

---

## Senior Dev Q&A — Program 10 (URL Shortener)

### Q1: Why Base62 and not Base64?
**A:** Base64 includes characters like `+`, `/`, and `=` which are not URL-safe. They would need to be percent-encoded in a browser URL (e.g., `%2F`), making the short link ugly and longer. Base62 uses only `[0-9, a-z, A-Z]` which are all perfectly safe in a URL without any encoding.

### Q2: What happens if two users try to shorten different URLs at the exact same time and get the same random code?
**A:** This is called a "collision." Our code handles it in two ways:
- **Application Level:** We check `shortCodeExists()` before inserting and retry up to 5 times.
- **Database Level:** The `short_code` column has a `UNIQUE` constraint. Even if our application check somehow misses it (a race condition between two servers), MySQL itself will reject the duplicate insert with a `DuplicateKeyException`, so data integrity is never compromised.

### Q3: Why use `SecureRandom` instead of `Random`?
**A:** `java.util.Random` uses a predictable algorithm (Linear Congruential Generator). If an attacker knows one generated code, they can mathematically predict future codes and potentially access private short URLs. `SecureRandom` uses the operating system's entropy source (like `/dev/urandom` on Linux) making it cryptographically unpredictable.

### Q4: Why do you increment the click count inside SQL instead of doing it in Java?
**A:** If we did it in Java, the flow would be: `SELECT click_count` → add 1 in Java → `UPDATE click_count`. If two users click simultaneously, both would read `click_count = 5`, both would calculate `6`, and both would write `6`. We just lost a click. By doing `SET click_count = click_count + 1` directly in SQL, the database engine handles the concurrency internally using row-level locks, guaranteeing every click is counted.

### Q5: This approach generates codes randomly. What's another approach used in production?
**A:** In production, many URL shorteners use the auto-incremented database ID and convert it to Base62. For example, ID `12345` → Base62 → `dnh`. This guarantees uniqueness (no collision detection needed) and is deterministic. The downside is that the codes are sequential, so an attacker could enumerate all short URLs by incrementing the code. The random approach we used is more secure but requires collision handling.

### Q6: How would you scale this to handle millions of URLs?
**A:** Three things:
- **Add an index** on the `short_code` column (we already have UNIQUE which creates an index).
- **Use database connection pooling** (like HikariCP) instead of opening a new connection per request.
- **Add an L1 cache** (like Caffeine, just like we did in Program 5) to cache the most frequently clicked short URLs in RAM so the database isn't hit on every single click.

---

## Senior Dev Q&A — Program 11 (Password Vault)

### Q1: Why AES and not RSA?
**A:** AES is a **symmetric** algorithm (same key encrypts and decrypts). RSA is **asymmetric** (public key encrypts, private key decrypts). For a password vault where the same application both writes and reads the data, symmetric encryption is the correct choice. RSA is used when two *different* parties need to communicate (e.g., HTTPS). Additionally, AES is significantly faster than RSA for bulk data encryption.

### Q2: What is the difference between encryption and hashing?
**A:** 
- **Encryption** is reversible. You can get the original data back with the key. We use it here because the user needs to *see* their password again.
- **Hashing** is one-way. You can never get the original data back. Hashing is used for *login systems* (e.g., storing a user's login password). You don't need to show the user their login password — you just hash what they type and compare it to the stored hash.

### Q3: Why do you Base64 encode the encrypted bytes?
**A:** AES encryption produces raw binary bytes. Some of these bytes are non-printable control characters (like `0x00` null bytes). If you try to store raw bytes directly in a `VARCHAR` or `TEXT` column, the database may silently truncate or corrupt the data at the first null byte. Base64 converts the binary into safe ASCII characters (`A-Z`, `a-z`, `0-9`, `+`, `/`, `=`) that can be safely stored in any text column.

### Q4: The key is hardcoded. How would you handle this in production?
**A:** In production, the key should **never** exist in source code or version control. Options include:
- **Environment Variables:** `System.getenv("VAULT_SECRET_KEY")` — the key is set on the server, not in the code.
- **AWS KMS / Azure Key Vault:** The cloud provider manages the key. Your app requests decryption through an API, and the key never leaves the cloud hardware.
- **HashiCorp Vault:** A dedicated secrets management tool that provides keys on demand with automatic rotation.

### Q5: What happens if someone changes the secret key?
**A:** All previously encrypted passwords become **permanently unrecoverable**. AES decryption with the wrong key doesn't return garbled text — it throws a `javax.crypto.BadPaddingException`. This is why key management and key rotation strategies (re-encrypting all data with the new key before retiring the old one) are critical in production systems.

### Q6: Is AES-128 secure enough, or should we use AES-256?
**A:** AES-128 is considered secure by all modern standards, including the U.S. government (NSA approves it for SECRET-level data). AES-256 is required only for TOP SECRET classification. For a corporate application, AES-128 is more than sufficient. The difference is the key size: 128-bit = 16-byte key, 256-bit = 32-byte key. AES-256 is slightly slower due to more encryption rounds (14 vs 10).

### Q7: Why is the encryption done in the Service layer and not in the DAO?
**A:** This follows the **Separation of Concerns** principle. The DAO's only job is to talk to the database — it should not know or care about business logic like encryption. By keeping encryption in the Service layer:
- We can unit test the DAO independently with plain strings.
- We can swap the encryption algorithm (e.g., from AES to ChaCha20) without modifying a single line of database code.
- If we ever need to encrypt data for a different storage backend (like a file or Redis), the `AESEncryptor` utility is completely reusable.
