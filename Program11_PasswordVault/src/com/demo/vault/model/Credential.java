package com.demo.vault.model;

public class Credential {
    private int id;
    private String serviceName;
    private String username;
    private String encryptedPassword; // What the DB stores (gibberish)
    private String decryptedPassword; // What the user sees (plain text, only in memory)

    public Credential() {}

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getServiceName() { return serviceName; }
    public void setServiceName(String serviceName) { this.serviceName = serviceName; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getEncryptedPassword() { return encryptedPassword; }
    public void setEncryptedPassword(String encryptedPassword) { this.encryptedPassword = encryptedPassword; }

    public String getDecryptedPassword() { return decryptedPassword; }
    public void setDecryptedPassword(String decryptedPassword) { this.decryptedPassword = decryptedPassword; }

    @Override
    public String toString() {
        return String.format("Service: %-15s | User: %-15s | Encrypted: %s", serviceName, username, encryptedPassword);
    }
}
