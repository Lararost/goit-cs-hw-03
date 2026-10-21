"""Faker: додати користувачів і завдання, зберігаючи попередні дані."""
import random
import sys
from uuid import uuid4
import psycopg
from faker import Faker
from create_tables import DATABASE_URL

def seed():
    """Додати 20 користувачів та 60 завдань; останні 3 без завдань.

    Повторний запуск додає нову порцію даних, не очищає таблиці.
    """
    fake = Faker()
    with psycopg.connect(DATABASE_URL) as conn:
        for name in ("new", "in progress", "completed"):
            conn.execute("INSERT INTO status(name) VALUES (%s) ON CONFLICT(name) DO NOTHING", (name,))
        statuses = dict(conn.execute("SELECT name, id FROM status").fetchall())
        user_ids = []
        for i in range(20):
            domain = "example.com" if i % 2 == 0 else "mail.test"
            email = f"{uuid4().hex}@{domain}"
            user_id = conn.execute(
                "INSERT INTO users(fullname,email) VALUES (%s,%s) RETURNING id",
                (fake.name()[:100], email),
            ).fetchone()[0]
            user_ids.append(user_id)
        for i in range(60):
            name = ("new", "in progress", "completed")[i % 3]
            description = None if i % 7 == 0 else ("" if i % 11 == 0 else fake.paragraph())
            conn.execute(
                "INSERT INTO tasks(title,description,status_id,user_id) VALUES (%s,%s,%s,%s)",
                (fake.sentence(nb_words=6)[:100], description, statuses[name],
                 user_ids[i if i < 17 else random.randrange(17)]),
            )
    print("Додано 20 користувачів і 60 завдань. Статуси: new, in progress, completed.")

if __name__ == "__main__":
    try:
        seed()
    except psycopg.Error:
        print("Помилка наповнення БД. Спочатку запустіть create_tables.py; перевірте з'єднання.", file=sys.stderr)
        sys.exit(1)
