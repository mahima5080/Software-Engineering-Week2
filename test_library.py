import unittest
import os
from library_manager import (
    DatabaseConnection,
    BookFactory,
    PrintedBook,
    EBook,
    AudioBook,
    LibraryManager,
    Observer,
)


class TestObserver(Observer):
    def __init__(self):
        self.messages = []

    def update(self, message: str) -> None:
        self.messages.append(message)


class TestLibraryManagementSystem(unittest.TestCase):
    TEST_DB = "test_library.db"

    def setUp(self):
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)
        self.library = LibraryManager(db_name=self.TEST_DB)
        self.test_observer = TestObserver()
        self.library.attach(self.test_observer)

    def tearDown(self):
        # Close connection to allow database file removal
        db_conn = DatabaseConnection(self.TEST_DB)
        db_conn.connection.close()
        DatabaseConnection._instance = None
        if os.path.exists(self.TEST_DB):
            os.remove(self.TEST_DB)

    def test_singleton_database_connection(self):
        """Test that DatabaseConnection returns a single instance."""
        db1 = DatabaseConnection(self.TEST_DB)
        db2 = DatabaseConnection(self.TEST_DB)
        self.assertIs(db1, db2)

    def test_factory_book_creation(self):
        """Test Factory pattern for different book types."""
        b1 = BookFactory.create_book(1, "Python 101", "Guido", "Printed", "300")
        b2 = BookFactory.create_book(2, "Clean Code", "Robert", "EBook", "5.2")
        b3 = BookFactory.create_book(3, "Design Patterns", "Gang of Four", "AudioBook", "120")

        self.assertIsInstance(b1, PrintedBook)
        self.assertIsInstance(b2, EBook)
        self.assertIsInstance(b3, AudioBook)

    def test_crud_and_observer(self):
        """Test full CRUD operations and Observer notifications."""
        # Create
        book = self.library.add_book("Data Structures", "Author A", "Printed", "450")
        self.assertEqual(len(self.test_observer.messages), 1)
        self.assertIn("New book added", self.test_observer.messages[0])

        # Read
        books = self.library.get_all_books()
        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].title, "Data Structures")

        # Update
        updated = self.library.update_book(book.book_id, "Advanced DS", "Author A", "Printed", "500")
        self.assertTrue(updated)
        self.assertEqual(len(self.test_observer.messages), 2)
        self.assertIn("updated", self.test_observer.messages[1])

        # Delete
        deleted = self.library.delete_book(book.book_id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.test_observer.messages), 3)
        self.assertIn("removed", self.test_observer.messages[2])


if __name__ == "__main__":
    unittest.main()