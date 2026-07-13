package com.demo.library.model;

public class Book {
    private int bookId;
    private String title;
    private int availableCopies;

    public Book(int bookId, String title, int availableCopies) {
        this.bookId = bookId;
        this.title = title;
        this.availableCopies = availableCopies;
    }

    @Override
    public String toString() {
        return "Book [ID=" + bookId + ", Title='" + title + "', Available=" + availableCopies + "]";
    }
}
