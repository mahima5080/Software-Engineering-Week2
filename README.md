# Library Management System (Software Engineering — Week 2)

A Python-based Library Management CLI Application implementing fundamental software engineering design patterns and database persistence.

---

## 📌 Design Patterns Implemented

1. **Singleton Pattern (`DatabaseConnection`):** Guarantees a single database connection throughout the application lifecycle.
2. **Factory Pattern (`BookFactory`):** Encapsulates object creation for various book types (`PrintedBook`, `EBook`, `AudioBook`).
3. **Observer Pattern (`NotificationSubject` & `Observer`):** Sends automated notification updates (Email & SMS) upon CRUD events.

---

## 🚀 How to Run the Application & Tests

1. **Run the CLI Application:**
   ```bash
   python library_manager.py
