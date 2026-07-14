package com.demo.apicache.model;

public class CacheEntry {
    private String endpoint;
    private String response;
    private long timestampMs;

    public CacheEntry(String endpoint, String response, long timestampMs) {
        this.endpoint = endpoint;
        this.response = response;
        this.timestampMs = timestampMs;
    }

    public String getEndpoint() { return endpoint; }
    public String getResponse() { return response; }
    public long getTimestampMs() { return timestampMs; }
}
