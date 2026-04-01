"""Create and seed examples/sample.db with realistic demo data."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "sample.db"


def create_sample_db() -> None:
    """Drop and recreate all demo tables, then seed them with 10 rows each.

    Writes the SQLite file to examples/sample.db relative to this script.
    Prints a confirmation line with the total row count when finished.
    """
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS orders;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS users;

        CREATE TABLE users (
            id         INTEGER PRIMARY KEY,
            name       TEXT    NOT NULL,
            email      TEXT    NOT NULL,
            created_at TEXT    NOT NULL
        );

        CREATE TABLE products (
            id       INTEGER PRIMARY KEY,
            name     TEXT    NOT NULL,
            price    REAL    NOT NULL,
            category TEXT    NOT NULL
        );

        CREATE TABLE orders (
            id         INTEGER PRIMARY KEY,
            user_id    INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity   INTEGER NOT NULL,
            total      REAL    NOT NULL
        );
    """)

    users = [
        (1, "Alice Johnson", "alice@example.com", "2024-01-15"),
        (2, "Bob Smith", "bob@example.com", "2024-01-20"),
        (3, "Carol White", "carol@example.com", "2024-02-01"),
        (4, "David Brown", "david@example.com", "2024-02-10"),
        (5, "Eve Davis", "eve@example.com", "2024-02-15"),
        (6, "Frank Miller", "frank@example.com", "2024-03-01"),
        (7, "Grace Wilson", "grace@example.com", "2024-03-10"),
        (8, "Henry Moore", "henry@example.com", "2024-03-15"),
        (9, "Iris Taylor", "iris@example.com", "2024-04-01"),
        (10, "Jack Anderson", "jack@example.com", "2024-04-10"),
    ]
    cur.executemany("INSERT INTO users VALUES (?,?,?,?)", users)

    products = [
        (1, "Laptop Pro", 1299.99, "Electronics"),
        (2, "Wireless Mouse", 29.99, "Electronics"),
        (3, "Mechanical Keyboard", 89.99, "Electronics"),
        (4, "USB-C Hub", 49.99, "Electronics"),
        (5, 'Monitor 27"', 399.99, "Electronics"),
        (6, "Python Crash Course", 34.99, "Books"),
        (7, "Clean Code", 39.99, "Books"),
        (8, "Standing Desk", 299.99, "Furniture"),
        (9, "Ergonomic Chair", 449.99, "Furniture"),
        (10, "Desk Lamp", 24.99, "Accessories"),
    ]
    cur.executemany("INSERT INTO products VALUES (?,?,?,?)", products)

    orders = [
        (1, 1, 1, 1, 1299.99),
        (2, 1, 2, 2, 59.98),
        (3, 2, 3, 1, 89.99),
        (4, 3, 6, 1, 34.99),
        (5, 4, 5, 1, 399.99),
        (6, 5, 9, 1, 449.99),
        (7, 6, 4, 3, 149.97),
        (8, 7, 7, 1, 39.99),
        (9, 8, 10, 2, 49.98),
        (10, 9, 8, 1, 299.99),
    ]
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", orders)

    conn.commit()
    conn.close()

    total = len(users) + len(products) + len(orders)
    print(f"sample.db created at {DB_PATH} with {total} rows across 3 tables")


if __name__ == "__main__":
    create_sample_db()
