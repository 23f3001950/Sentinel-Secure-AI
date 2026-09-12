import sqlite3
from pathlib import Path
from datetime import datetime


DATABASE_PATH = Path(__file__).parent / "sentinel_secure.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_count INTEGER NOT NULL,
            international INTEGER NOT NULL,
            unusual_hour INTEGER NOT NULL,
            new_device INTEGER NOT NULL,
            risk_score INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def create_user(username, email, password_hash):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users
            (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                username,
                email,
                password_hash,
                datetime.now().isoformat()
            )
        )

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        connection.close()


def get_user_by_email(email):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


def save_transaction(
    user_id,
    amount,
    transaction_count,
    international,
    unusual_hour,
    new_device,
    risk_score,
    risk_level
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO transactions (
            user_id,
            amount,
            transaction_count,
            international,
            unusual_hour,
            new_device,
            risk_score,
            risk_level,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            amount,
            transaction_count,
            int(international),
            int(unusual_hour),
            int(new_device),
            risk_score,
            risk_level,
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


def get_user_transactions(user_id):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM transactions
        WHERE user_id = ?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    transactions = cursor.fetchall()

    connection.close()

    return transactions
