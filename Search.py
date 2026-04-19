"""Search functionality for the Library Management System."""

from library import Library
from book import Book



def search_by_title(library: Library, title: str) -> list[Book]:
    """Search books by title."""
    title = title.lower().strip()
    return [book for book in library.list_books() if title in book.title.lower()]



def search_by_author(library: Library, author: str) -> list[Book]:
    """Search books by author."""
    author = author.lower().strip()
    return [book for book in library.list_books() if author in book.author.lower()]



def search_by_isbn(library: Library, isbn: str) -> Book | None:
    """Search a book by ISBN."""
    return library.get_book(isbn.strip())
