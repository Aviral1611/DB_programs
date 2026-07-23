package com.demo.vault.main;

import com.demo.vault.service.VaultService;

public class VaultMain {
    public static void main(String[] args) {
        System.out.println("=== Secure Password Vault (AES-128 Encryption) ===\n");
        VaultService service = new VaultService();

        // Clean slate
        service.clearData();

        // 1. Store credentials (passwords get encrypted before hitting the DB)
        System.out.println("[Step 1] Storing credentials securely...");
        service.storeCredential("Gmail", "aviral.bansal", "MyGmail@2026!");
        service.storeCredential("GitHub", "aviral-dev", "GitP@ss#Secure99");
        service.storeCredential("AWS Console", "admin", "Aws!Root$Key2026");

        // 2. Show what the database actually stores (encrypted gibberish)
        service.displayDatabaseView();

        // 3. Retrieve and decrypt specific credentials
        System.out.println("\n[Step 3] Retrieving and decrypting credentials...");
        service.retrieveCredential("Gmail", "aviral.bansal");
        System.out.println();
        service.retrieveCredential("GitHub", "aviral-dev");
        System.out.println();
        service.retrieveCredential("AWS Console", "admin");

        // 4. Try retrieving a non-existent credential
        System.out.println("\n[Step 4] Attempting to retrieve a non-existent credential...");
        service.retrieveCredential("Netflix", "someone");
    }
}
