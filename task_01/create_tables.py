"""Створення таблиць у наявній PostgreSQL базі (її створює Docker)."""
import os
import sys
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:hw03pass@localhost:5433/task_manager")
DDL = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    status_id INTEGER NOT NULL REFERENCES status(id),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE
);
"""

def create_tables():
    """Створити схему без видалення наявних даних."""
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute(DDL)

if __name__ == "__main__":
    try:
        create_tables()
        print("Таблиці users, status, tasks створено.")
    except psycopg.Error:
        print("Не вдалося створити таблиці. Перевірте PostgreSQL і DATABASE_URL.", file=sys.stderr)
        sys.exit(1)
