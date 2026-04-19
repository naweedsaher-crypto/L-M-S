"""Tkinter GUI for the Library Management System."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from auth_system import authenticate, get_role
from book import Book
from issue_return import issue_book, return_book
from library import Library
from member import Member
from search import search_by_author, search_by_isbn, search_by_title


class LoginWindow:
    """Simple login window shown before the main application."""

    def __init__(self, root: tk.Tk, on_success) -> None:
        self.root = root
        self.on_success = on_success

        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(fill="both", expand=True)

        ttk.Label(
            self.frame,
            text="Library Management System",
            font=("Arial", 16, "bold"),
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        ttk.Label(self.frame, text="Username:").grid(row=1, column=0, sticky="w", pady=6)
        self.username_entry = ttk.Entry(self.frame, width=28)
        self.username_entry.grid(row=1, column=1, pady=6)

        ttk.Label(self.frame, text="Password:").grid(row=2, column=0, sticky="w", pady=6)
        self.password_entry = ttk.Entry(self.frame, width=28, show="*")
        self.password_entry.grid(row=2, column=1, pady=6)

        ttk.Button(self.frame, text="Login", command=self.login).grid(
            row=3, column=0, columnspan=2, pady=(12, 8)
        )

        info = "Default users: admin/admin123 and member/member123"
        ttk.Label(self.frame, text=info).grid(row=4, column=0, columnspan=2)

        self.username_entry.focus_set()
        self.root.bind("<Return>", lambda _event: self.login())

    def login(self) -> None:
        """Validate credentials and open the main app."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if authenticate(username, password):
            role = get_role(username) or "unknown"
            self.frame.destroy()
            self.on_success(username, role)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")


class LibraryGUI:
    """Main Tkinter interface for library management."""

    def __init__(self, root: tk.Tk, username: str, role: str) -> None:
        self.root = root
        self.username = username
        self.role = role
        self.library = Library()
        self.status_var = tk.StringVar(value=f"Logged in as {username} ({role})")

        self.seed_sample_data()
        self.setup_window()
        self.create_widgets()
        self.refresh_all_views()

    def setup_window(self) -> None:
        self.root.title("Library Management System - GUI")
        self.root.geometry("980x700")
        self.root.minsize(900, 620)

    def seed_sample_data(self) -> None:
        """Load sample data for demonstration."""
        sample_books = [
            Book("101", "Python Basics", "John Smith", 3),
            Book("102", "Data Structures", "Alice Johnson", 2),
            Book("103", "Machine Learning", "David Lee", 1),
        ]
        for book in sample_books:
            self.library.add_book(book)

        sample_members = [
            Member("M001", "Ali"),
            Member("M002", "Sara"),
        ]
        for member in sample_members:
            try:
                self.library.register_member(member)
            except ValueError:
                pass

    def create_widgets(self) -> None:
        """Build all visible UI widgets."""
        header = ttk.Frame(self.root, padding=(15, 12))
        header.pack(fill="x")

        ttk.Label(
            header,
            text="Library Management System",
            font=("Arial", 18, "bold"),
        ).pack(side="left")
        ttk.Label(header, textvariable=self.status_var).pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.books_tab = ttk.Frame(self.notebook, padding=12)
        self.members_tab = ttk.Frame(self.notebook, padding=12)
        self.search_tab = ttk.Frame(self.notebook, padding=12)
        self.transactions_tab = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.books_tab, text="Books")
        self.notebook.add(self.members_tab, text="Members")
        self.notebook.add(self.search_tab, text="Search")
        self.notebook.add(self.transactions_tab, text="Issue / Return")

        self.build_books_tab()
        self.build_members_tab()
        self.build_search_tab()
        self.build_transactions_tab()

        footer = ttk.Frame(self.root, padding=(12, 0, 12, 10))
        footer.pack(fill="x")
        ttk.Label(footer, text="Status:").pack(side="left")
        ttk.Label(footer, textvariable=self.status_var).pack(side="left", padx=(6, 0))

    def build_books_tab(self) -> None:
        """Create the books tab UI."""
        form = ttk.LabelFrame(self.books_tab, text="Add Book", padding=12)
        form.pack(fill="x", pady=(0, 10))

        labels = ["ISBN", "Title", "Author", "Copies"]
        self.book_entries: dict[str, ttk.Entry] = {}
        for index, label in enumerate(labels):
            ttk.Label(form, text=f"{label}:").grid(row=index, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=40)
            entry.grid(row=index, column=1, sticky="w", pady=5, padx=(8, 0))
            self.book_entries[label.lower()] = entry

        ttk.Button(form, text="Add Book", command=self.add_book).grid(
            row=4, column=0, columnspan=2, pady=(10, 0)
        )

        list_frame = ttk.LabelFrame(self.books_tab, text="Book List", padding=12)
        list_frame.pack(fill="both", expand=True)

        columns = ("isbn", "title", "author", "copies")
        self.books_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for col, title, width in [
            ("isbn", "ISBN", 130),
            ("title", "Title", 280),
            ("author", "Author", 220),
            ("copies", "Copies", 90),
        ]:
            self.books_tree.heading(col, text=title)
            self.books_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.books_tree.yview)
        self.books_tree.configure(yscrollcommand=scrollbar.set)
        self.books_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def build_members_tab(self) -> None:
        """Create the members tab UI."""
        form = ttk.LabelFrame(self.members_tab, text="Register Member", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Member ID:").grid(row=0, column=0, sticky="w", pady=5)
        self.member_id_entry = ttk.Entry(form, width=40)
        self.member_id_entry.grid(row=0, column=1, sticky="w", pady=5, padx=(8, 0))

        ttk.Label(form, text="Name:").grid(row=1, column=0, sticky="w", pady=5)
        self.member_name_entry = ttk.Entry(form, width=40)
        self.member_name_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(8, 0))

        ttk.Button(form, text="Register Member", command=self.register_member).grid(
            row=2, column=0, columnspan=2, pady=(10, 0)
        )

        list_frame = ttk.LabelFrame(self.members_tab, text="Member List", padding=12)
        list_frame.pack(fill="both", expand=True)

        columns = ("member_id", "name", "borrowed_books")
        self.members_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for col, title, width in [
            ("member_id", "Member ID", 150),
            ("name", "Name", 220),
            ("borrowed_books", "Borrowed Books", 420),
        ]:
            self.members_tree.heading(col, text=title)
            self.members_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.members_tree.yview)
        self.members_tree.configure(yscrollcommand=scrollbar.set)
        self.members_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def build_search_tab(self) -> None:
        """Create the search tab UI."""
        form = ttk.LabelFrame(self.search_tab, text="Search Books", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="Search by:").grid(row=0, column=0, sticky="w", pady=5)
        self.search_type = tk.StringVar(value="title")
        search_combo = ttk.Combobox(
            form,
            textvariable=self.search_type,
            values=["title", "author", "isbn"],
            state="readonly",
            width=18,
        )
        search_combo.grid(row=0, column=1, sticky="w", pady=5, padx=(8, 0))

        ttk.Label(form, text="Keyword:").grid(row=1, column=0, sticky="w", pady=5)
        self.search_entry = ttk.Entry(form, width=40)
        self.search_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(8, 0))

        ttk.Button(form, text="Search", command=self.search_books).grid(
            row=2, column=0, columnspan=2, pady=(10, 0)
        )

        list_frame = ttk.LabelFrame(self.search_tab, text="Search Results", padding=12)
        list_frame.pack(fill="both", expand=True)

        columns = ("isbn", "title", "author", "copies")
        self.search_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        for col, title, width in [
            ("isbn", "ISBN", 130),
            ("title", "Title", 280),
            ("author", "Author", 220),
            ("copies", "Copies", 90),
        ]:
            self.search_tree.heading(col, text=title)
            self.search_tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.search_tree.yview)
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        self.search_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def build_transactions_tab(self) -> None:
        """Create the issue/return tab UI."""
        form = ttk.LabelFrame(self.transactions_tab, text="Issue or Return Book", padding=12)
        form.pack(fill="x", pady=(0, 10))

        ttk.Label(form, text="ISBN:").grid(row=0, column=0, sticky="w", pady=5)
        self.transaction_isbn_entry = ttk.Entry(form, width=40)
        self.transaction_isbn_entry.grid(row=0, column=1, sticky="w", pady=5, padx=(8, 0))

        ttk.Label(form, text="Member ID:").grid(row=1, column=0, sticky="w", pady=5)
        self.transaction_member_entry = ttk.Entry(form, width=40)
        self.transaction_member_entry.grid(row=1, column=1, sticky="w", pady=5, padx=(8, 0))

        button_row = ttk.Frame(form)
        button_row.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="w")
        ttk.Button(button_row, text="Issue Book", command=self.issue_book_action).pack(side="left")
        ttk.Button(button_row, text="Return Book", command=self.return_book_action).pack(
            side="left", padx=(10, 0)
        )

        help_frame = ttk.LabelFrame(self.transactions_tab, text="Quick Help", padding=12)
        help_frame.pack(fill="x")
        help_text = (
            "1. Enter the book ISBN.\n"
            "2. Enter the member ID.\n"
            "3. Click 'Issue Book' to borrow the book.\n"
            "4. Click 'Return Book' to return the book."
        )
        ttk.Label(help_frame, text=help_text, justify="left").pack(anchor="w")

    def add_book(self) -> None:
        """Read form input and add a book."""
        try:
            isbn = self.book_entries["isbn"].get().strip()
            title = self.book_entries["title"].get().strip()
            author = self.book_entries["author"].get().strip()
            copies_text = self.book_entries["copies"].get().strip()

            if not all([isbn, title, author, copies_text]):
                raise ValueError("Please fill in all book fields.")

            copies = int(copies_text)
            self.library.add_book(Book(isbn, title, author, copies))
            self.clear_entries(self.book_entries.values())
            self.refresh_books_tree()
            self.refresh_search_results([])
            self.set_status(f"Book '{title}' added successfully.")
            messagebox.showinfo("Success", "Book added successfully.")
        except ValueError as error:
            messagebox.showerror("Input Error", str(error))

    def register_member(self) -> None:
        """Read form input and register a member."""
        member_id = self.member_id_entry.get().strip()
        name = self.member_name_entry.get().strip()

        try:
            if not member_id or not name:
                raise ValueError("Please enter both member ID and name.")

            self.library.register_member(Member(member_id, name))
            self.member_id_entry.delete(0, tk.END)
            self.member_name_entry.delete(0, tk.END)
            self.refresh_members_tree()
            self.set_status(f"Member '{name}' registered successfully.")
            messagebox.showinfo("Success", "Member registered successfully.")
        except ValueError as error:
            messagebox.showerror("Input Error", str(error))

    def search_books(self) -> None:
        """Search books based on the selected search type."""
        keyword = self.search_entry.get().strip()
        search_type = self.search_type.get()

        if not keyword:
            messagebox.showwarning("Missing Input", "Please enter a search keyword.")
            return

        if search_type == "title":
            results = search_by_title(self.library, keyword)
        elif search_type == "author":
            results = search_by_author(self.library, keyword)
        else:
            book = search_by_isbn(self.library, keyword)
            results = [book] if book else []

        self.refresh_search_results(results)
        self.set_status(f"Found {len(results)} matching book(s).")

    def issue_book_action(self) -> None:
        """Issue a book through the business logic layer."""
        isbn = self.transaction_isbn_entry.get().strip()
        member_id = self.transaction_member_entry.get().strip()
        result = issue_book(self.library, isbn, member_id)
        self.after_transaction(result)

    def return_book_action(self) -> None:
        """Return a book through the business logic layer."""
        isbn = self.transaction_isbn_entry.get().strip()
        member_id = self.transaction_member_entry.get().strip()
        result = return_book(self.library, isbn, member_id)
        self.after_transaction(result)

    def after_transaction(self, message: str) -> None:
        """Refresh UI after issuing or returning a book."""
        self.refresh_books_tree()
        self.refresh_members_tree()
        self.transaction_isbn_entry.delete(0, tk.END)
        self.transaction_member_entry.delete(0, tk.END)
        self.set_status(message)

        if "not found" in message.lower() or "did not borrow" in message.lower() or "no copies" in message.lower():
            messagebox.showwarning("Action Result", message)
        else:
            messagebox.showinfo("Action Result", message)

    def refresh_all_views(self) -> None:
        """Refresh all Treeview widgets."""
        self.refresh_books_tree()
        self.refresh_members_tree()
        self.refresh_search_results([])

    def refresh_books_tree(self) -> None:
        """Reload all rows in the books table."""
        self.clear_tree(self.books_tree)
        for book in self.library.list_books():
            self.books_tree.insert("", tk.END, values=(book.isbn, book.title, book.author, book.copies))

    def refresh_members_tree(self) -> None:
        """Reload all rows in the members table."""
        self.clear_tree(self.members_tree)
        for member in self.library.list_members():
            borrowed = ", ".join(member.borrowed_books) if member.borrowed_books else "None"
            self.members_tree.insert("", tk.END, values=(member.member_id, member.name, borrowed))

    def refresh_search_results(self, books: list[Book]) -> None:
        """Reload search results table."""
        self.clear_tree(self.search_tree)
        for book in books:
            self.search_tree.insert("", tk.END, values=(book.isbn, book.title, book.author, book.copies))

    def clear_tree(self, tree: ttk.Treeview) -> None:
        """Remove all rows from a Treeview widget."""
        for item in tree.get_children():
            tree.delete(item)

    def clear_entries(self, entries) -> None:
        """Clear multiple Entry widgets."""
        for entry in entries:
            entry.delete(0, tk.END)

    def set_status(self, message: str) -> None:
        """Update the footer status line."""
        self.status_var.set(message)


def launch_gui() -> None:
    """Start the GUI application."""
    root = tk.Tk()

    def open_main_app(username: str, role: str) -> None:
        LibraryGUI(root, username, role)

    LoginWindow(root, open_main_app)
    root.mainloop()


if __name__ == "__main__":
    launch_gui()
