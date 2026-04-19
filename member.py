"""Member module for the Library Management System."""


class Member:
    """Represents a library member."""

    def __init__(self, member_id: str, name: str) -> None:
        self.member_id = member_id.strip()
        self.name = name.strip()
        self.borrowed_books: list[str] = []

    def borrow_book(self, isbn: str) -> None:
        """Add a borrowed book ISBN to the member record."""
        self.borrowed_books.append(isbn)

    def return_book(self, isbn: str) -> None:
        """Remove a returned book ISBN from the member record."""
        if isbn not in self.borrowed_books:
            raise ValueError("this member did not borrow the given book")
        self.borrowed_books.remove(isbn)

    def __str__(self) -> str:
        borrowed = ", ".join(self.borrowed_books) if self.borrowed_books else "None"
        return f"Member ID: {self.member_id} | Name: {self.name} | Borrowed: {borrowed}"
