"""
Software Engineering - Week 2 Mini Project
Library Management System using Design Patterns:
- Singleton: Database Connection Manager (SQLite)
- Factory: Book Creation Factory (PrintedBook, EBook, AudioBook)
- Observer: Event Notification System (Email & SMS Observers)
- CLI Interface & CRUD Operations
"""

import sqlite3
from abc import ABC, abstractmethod


# =============================================================================
# 1. SINGLETON PATTERN: Database Connection Manager
# =============================================================================

class DatabaseConnection:
    _instance = None

    def __new__(cls, db_name="library.db"):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance.connection = sqlite3.connect(db_name)
            cls._instance._create_tables()
        return cls._instance

    def _create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                book_type TEXT NOT NULL,
                extra_info TEXT NOT NULL
            )
        """)
        self.connection.commit()

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()


# =============================================================================
# 2. FACTORY PATTERN: Book Hierarchy & Factory
# =============================================================================

class Book(ABC):
    def __init__(self, book_id: int, title: str, author: str, book_type: str):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.book_type = book_type

    @abstractmethod
    def get_details(self) -> str:
        pass


class PrintedBook(Book):
    def __init__(self, book_id: int, title: str, author: str, pages: str):
        super().__init__(book_id, title, author, "Printed")
        self.pages = pages

    def get_details(self) -> str:
        return f"[Printed] ID: {self.book_id} | Title: '{self.title}' | Author: {self.author} | Pages: {self.pages}"


class EBook(Book):
    def __init__(self, book_id: int, title: str, author: str, file_size_mb: str):
        super().__init__(book_id, title, author, "EBook")
        self.file_size_mb = file_size_mb

    def get_details(self) -> str:
        return f"[EBook] ID: {self.book_id} | Title: '{self.title}' | Author: {self.author} | Size: {self.file_size_mb} MB"


class AudioBook(Book):
    def __init__(self, book_id: int, title: str, author: str, duration_mins: str):
        super().__init__(book_id, title, author, "AudioBook")
        self.duration_mins = duration_mins

    def get_details(self) -> str:
        return f"[AudioBook] ID: {self.book_id} | Title: '{self.title}' | Author: {self.author} | Duration: {self.duration_mins} mins"


class BookFactory:
    @staticmethod
    def create_book(book_id: int, title: str, author: str, book_type: str, extra_info: str) -> Book:
        b_type = book_type.strip().lower()
        if b_type == "printed":
            return PrintedBook(book_id, title, author, extra_info)
        elif b_type == "ebook":
            return EBook(book_id, title, author, extra_info)
        elif b_type == "audiobook":
            return AudioBook(book_id, title, author, extra_info)
        else:
            raise ValueError(f"Unknown book type: {book_type}")


# =============================================================================
# 3. OBSERVER PATTERN: Notification System
# =============================================================================

class Observer(ABC):
    @abstractmethod
    def update(self, message: str) -> None:
        pass


class EmailNotificationObserver(Observer):
    def update(self, message: str) -> None:
        print(f"  📧 [Email Notification]: {message}")


class SMSNotificationObserver(Observer):
    def update(self, message: str) -> None:
        print(f"  📱 [SMS Notification]: {message}")


class NotificationSubject:
    def __init__(self):
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)

    def notify(self, message: str) -> None:
        for observer in self._observers:
            observer.update(message)


# =============================================================================
# 4. LIBRARY MANAGER (CRUD Logic)
# =============================================================================

class LibraryManager(NotificationSubject):
    def __init__(self, db_name="library.db"):
        super().__init__()
        self.db = DatabaseConnection(db_name)

    def add_book(self, title: str, author: str, book_type: str, extra_info: str) -> Book:
        cursor = self.db.get_cursor()
        cursor.execute(
            "INSERT INTO books (title, author, book_type, extra_info) VALUES (?, ?, ?, ?)",
            (title, author, book_type, extra_info)
        )
        self.db.commit()
        book_id = cursor.lastrowid
        book = BookFactory.create_book(book_id, title, author, book_type, extra_info)
        self.notify(f"New book added: '{title}' by {author} ({book_type})")
        return book

    def get_all_books(self) -> list[Book]:
        cursor = self.db.get_cursor()
        cursor.execute("SELECT id, title, author, book_type, extra_info FROM books")
        rows = cursor.fetchall()
        books = []
        for row in rows:
            books.append(BookFactory.create_book(row[0], row[1], row[2], row[3], row[4]))
        return books

    def update_book(self, book_id: int, title: str, author: str, book_type: str, extra_info: str) -> bool:
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE books SET title=?, author=?, book_type=?, extra_info=? WHERE id=?",
            (title, author, book_type, extra_info, book_id)
        )
        self.db.commit()
        if cursor.rowcount > 0:
            self.notify(f"Book ID #{book_id} has been updated to '{title}'")
            return True
        return False

    def delete_book(self, book_id: int) -> bool:
        cursor = self.db.get_cursor()
        cursor.execute("DELETE FROM books WHERE id=?", (book_id,))
        self.db.commit()
        if cursor.rowcount > 0:
            self.notify(f"Book ID #{book_id} was removed from the library database.")
            return True
        return False


# =============================================================================
# 5. CLI INTERFACE
# =============================================================================

def main():
    library = LibraryManager()
    
    # Attach default observers
    library.attach(EmailNotificationObserver())
    library.attach(SMSNotificationObserver())

    while True:
        print("\n==========================================")
        print("   📚 LIBRARY MANAGEMENT SYSTEM (CLI)")
        print("==========================================")
        print("1. View All Books (Read)")
        print("2. Add New Book (Create - Factory)")
        print("3. Update Book Details (Update)")
        print("4. Delete Book (Delete)")
        print("5. Exit")

        choice = input("Enter option (1-5): ").strip()

        if choice == "1":
            books = library.get_all_books()
            if not books:
                print("\nNo books found in the library database.")
            else:
                print("\n--- Library Collection ---")
                for b in books:
                    print(b.get_details())

        elif choice == "2":
            title = input("Enter Title: ").strip()
            author = input("Enter Author: ").strip()
            b_type = input("Enter Type (Printed / EBook / AudioBook): ").strip()
            
            if b_type.lower() == "printed":
                extra = input("Enter Page Count: ").strip()
            elif b_type.lower() == "ebook":
                extra = input("Enter File Size (MB): ").strip()
            elif b_type.lower() == "audiobook":
                extra = input("Enter Duration (Minutes): ").strip()
            else:
                print("Invalid book type!")
                continue

            try:
                library.add_book(title, author, b_type, extra)
                print("Book created successfully!")
            except Exception as e:
                print(f"Error creating book: {e}")

        elif choice == "3":
            try:
                book_id = int(input("Enter Book ID to update: "))
                title = input("Enter New Title: ").strip()
                author = input("Enter New Author: ").strip()
                b_type = input("Enter New Type (Printed / EBook / AudioBook): ").strip()
                extra = input("Enter New Extra Detail (Pages/Size/Duration): ").strip()
                
                if library.update_book(book_id, title, author, b_type, extra):
                    print("Book updated successfully!")
                else:
                    print("Book ID not found.")
            except ValueError:
                print("Please enter a numerical Book ID.")

        elif choice == "4":
            try:
                book_id = int(input("Enter Book ID to delete: "))
                if library.delete_book(book_id):
                    print("Book deleted successfully!")
                else:
                    print("Book ID not found.")
            except ValueError:
                print("Please enter a numerical Book ID.")

        elif choice == "5":
            print("Exiting Library Manager. Goodbye!")
            break
        else:
            print("Invalid selection. Try again.")


if __name__ == "__main__":
    main()