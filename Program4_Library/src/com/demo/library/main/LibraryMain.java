package com.demo.library.main;

import com.demo.library.service.LibraryService;

public class LibraryMain {
    public static void main(String[] args) {
        System.out.println("=== Library Book Checkout System ===");
        LibraryService service = new LibraryService();

        int book1984Id = 2; // 1 copy available
        int bookMockingbirdId = 3; // 0 copies available

        System.out.println("\n[Status Before Checkout]");
        service.displayBookStatus(book1984Id);
        service.displayBookStatus(bookMockingbirdId);

        System.out.println("\n[Attempting Checkouts]");
        service.borrowBook(book1984Id, "Alice");
        service.borrowBook(book1984Id, "Bob"); // Should fail, only 1 copy
        service.borrowBook(bookMockingbirdId, "Charlie"); // Should fail, 0 copies

        System.out.println("\n[Status After Checkout]");
        service.displayBookStatus(book1984Id);
        service.displayBookStatus(bookMockingbirdId);
    }
}
