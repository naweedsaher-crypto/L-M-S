"""Book module for the Library Management System."""

from dataclasses import dataclass


@dataclass
"""Book a module for the Library Management System."""


class Book:
    """Represents a book in the library."""

    def __init__(self, isbn, title, author, copies):
        if copies < 0:
            raise ValueError("Copies cannot be negative.")

        self.isbn = isbn
        self.title = title
        self.author = author
        self.copies = copies

    def is_available(self):
        """Return True if at least one copy is available."""
        return self.copies > 0

    def add_copies(self, count):
        """Add more copies to the book stock."""
        if count < 1:
            raise ValueError("Count must be at least 1.")
        self.copies += count

    def __str__(self):
        return f"ISBN: {self.isbn}, Title: {self.title}, Author: {self.author}, Copies: {self.copies}"