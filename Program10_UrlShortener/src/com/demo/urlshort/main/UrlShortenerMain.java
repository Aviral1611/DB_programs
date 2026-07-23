package com.demo.urlshort.main;

import com.demo.urlshort.service.UrlService;

public class UrlShortenerMain {
    public static void main(String[] args) {
        System.out.println("=== URL Shortener Service (Base62 Encoding) ===\n");
        UrlService service = new UrlService();

        // Clean slate
        service.clearData();

        // 1. Shorten some URLs
        System.out.println("[Step 1] Shortening URLs...");
        String code1 = service.shortenUrl("https://docs.google.com/spreadsheets/d/1a2b3c4d5e/edit?usp=sharing");
        System.out.println("  Long URL shortened to code: " + code1);

        String code2 = service.shortenUrl("https://www.amazon.in/dp/B0CXYZ1234/ref=sr_1_1?keywords=laptop&qid=1690000000");
        System.out.println("  Long URL shortened to code: " + code2);

        String code3 = service.shortenUrl("https://stackoverflow.com/questions/12345678/how-to-use-preparedstatement-in-java");
        System.out.println("  Long URL shortened to code: " + code3);

        // 2. Simulate clicks
        System.out.println("\n[Step 2] Simulating user clicks...");
        for (int i = 0; i < 5; i++) {
            String resolved = service.resolveUrl(code1);
            if (i == 0) System.out.println("  Clicking code '" + code1 + "' -> Redirects to: " + resolved);
        }
        System.out.println("  (Clicked code '" + code1 + "' 5 times total)");

        for (int i = 0; i < 2; i++) {
            service.resolveUrl(code2);
        }
        System.out.println("  (Clicked code '" + code2 + "' 2 times total)");

        service.resolveUrl(code3);
        System.out.println("  (Clicked code '" + code3 + "' 1 time total)");

        // 3. Display analytics
        service.displayAnalytics();
    }
}
