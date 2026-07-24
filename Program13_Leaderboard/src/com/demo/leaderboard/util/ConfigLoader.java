package com.demo.leaderboard.util;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Loads configuration from an external properties file.
 * Eliminates hardcoded values — ops teams can change settings
 * without recompiling the Java code.
 */
public class ConfigLoader {
    private static final Properties properties = new Properties();
    private static boolean loaded = false;

    public static synchronized void load() {
        if (loaded) return;

        try (InputStream input = new FileInputStream("config.properties")) {
            properties.load(input);
            loaded = true;
            System.out.println("[CONFIG] Loaded config.properties successfully.");
        } catch (IOException e) {
            System.err.println("[CONFIG ERROR] Failed to load config.properties: " + e.getMessage());
            throw new RuntimeException("Cannot start application without configuration.", e);
        }
    }

    public static String get(String key) {
        if (!loaded) load();
        String value = properties.getProperty(key);
        if (value == null) {
            throw new RuntimeException("[CONFIG ERROR] Missing required property: " + key);
        }
        return value.trim();
    }

    public static int getInt(String key) {
        return Integer.parseInt(get(key));
    }
}
