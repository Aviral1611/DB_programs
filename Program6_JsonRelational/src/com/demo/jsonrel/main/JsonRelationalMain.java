package com.demo.jsonrel.main;

import com.demo.jsonrel.service.JsonService;

public class JsonRelationalMain {
    public static void main(String[] args) {
        System.out.println("=== JSON to Relational DB Converter ===");
        JsonService service = new JsonService();

    
        String jsonPayload = 
            "[{\"id\":1, \"name\":\"Alice\", \"hobbies\":[\"reading\",\"hiking\"]}, " +
            "{\"id\":2, \"name\":\"Bob\", \"hobbies\":[\"gaming\"]}, " +
            "{\"id\":3, \"name\":\"Charlie\", \"hobbies\":[\"cooking\",\"traveling\",\"swimming\"]}]";

        System.out.println("Raw JSON Payload: " + jsonPayload + "\n");

        service.processJsonToDatabase(jsonPayload);
        service.showNormalizedData();
    }
}
