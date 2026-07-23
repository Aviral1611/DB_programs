package com.demo.urlshort.model;

import java.sql.Timestamp;

public class ShortUrl {
    private int id;
    private String shortCode;
    private String originalUrl;
    private int clickCount;
    private Timestamp createdAt;

    public ShortUrl() {}

    public ShortUrl(String shortCode, String originalUrl) {
        this.shortCode = shortCode;
        this.originalUrl = originalUrl;
    }

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getShortCode() { return shortCode; }
    public void setShortCode(String shortCode) { this.shortCode = shortCode; }

    public String getOriginalUrl() { return originalUrl; }
    public void setOriginalUrl(String originalUrl) { this.originalUrl = originalUrl; }

    public int getClickCount() { return clickCount; }
    public void setClickCount(int clickCount) { this.clickCount = clickCount; }

    public Timestamp getCreatedAt() { return createdAt; }
    public void setCreatedAt(Timestamp createdAt) { this.createdAt = createdAt; }

    @Override
    public String toString() {
        return String.format("Code: %s | Clicks: %d | URL: %s", shortCode, clickCount, originalUrl);
    }
}
