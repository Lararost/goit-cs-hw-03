"""Інтеграційна перевірка після create_tables.py та seed.py."""
import importlib.util
import os
from pathlib import Path
import sys
from uuid import uuid4
import psycopg
from pymongo import MongoClient

ROOT = Path(__file__).parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def verify_postgres():
    """Перевірити FK, UNIQUE і SQL; тестові рядки відкочуються."""
    schema = load("schema", ROOT / "task_01/create_tables.py")
    with psycopg.connect(schema.DATABASE_URL, autocommit=True) as conn:
        assert conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] >= 20
        assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] >= 60
        assert set(r[0] for r in conn.execute("SELECT name FROM status")) >= {"new", "in progress", "completed"}
        conn.execute("BEGIN")
        try:
            email = f"{uuid4().hex}@test.invalid"
            uid = conn.execute("INSERT INTO users(fullname,email) VALUES ('Test',%s) RETURNING id", (email,)).fetchone()[0]
            conn.execute("SAVEPOINT unique_test")
            try:
                conn.execute("INSERT INTO users(fullname,email) VALUES ('Duplicate',%s)", (email,))
            except psycopg.errors.UniqueViolation:
                conn.execute("ROLLBACK TO SAVEPOINT unique_test")
            else:
                raise AssertionError("email UNIQUE відсутнє")
            conn.execute("SAVEPOINT status_test")
            try:
                conn.execute("INSERT INTO status(name) VALUES ('new')")
            except psycopg.errors.UniqueViolation:
                conn.execute("ROLLBACK TO SAVEPOINT status_test")
            else:
                raise AssertionError("status.name UNIQUE відсутнє")
            tid = conn.execute("INSERT INTO tasks(title,user_id,status_id) VALUES ('Test',%s,(SELECT id FROM status WHERE name='new')) RETURNING id", (uid,)).fetchone()[0]
            conn.execute("DELETE FROM users WHERE id=%s", (uid,))
            assert conn.execute("SELECT COUNT(*) FROM tasks WHERE id=%s", (tid,)).fetchone()[0] == 0
        finally:
            conn.execute("ROLLBACK")
        # Весь файл містить власні BEGIN і ROLLBACK.
        with conn.cursor() as cur:
            cur.execute((ROOT / "task_01/queries.sql").read_text(), prepare=False)
            while cur.nextset():
                pass
    print("PostgreSQL: дані, UNIQUE, CASCADE та всі SQL-запити — OK")

def verify_mongo():
    """CRUD у тимчасовій колекції; робочі cats не змінюються."""
    app = load("cats", ROOT / "task_02/main.py")
    with MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27018/"), serverSelectionTimeoutMS=5000) as client:
        client.admin.command("ping")
        coll = client[os.getenv("MONGODB_DB", "hw03")]["verify_" + uuid4().hex]
        try:
            coll.create_index("name", unique=True)
            app.create_cat(coll, "Barsik", 3, ["рудий"])
            assert len(app.read_all(coll)) == 1
            assert app.read_by_name(coll, "barsik")["age"] == 3
            assert app.update_age(coll, "barsik", 4).modified_count == 1
            app.add_feature(coll, "barsik", "лагідний")
            app.add_feature(coll, "barsik", "лагідний")
            assert app.read_by_name(coll, "barsik")["features"].count("лагідний") == 1
            assert app.delete_by_name(coll, "barsik") == 1
            assert app.read_by_name(coll, "barsik") is None
            app.create_cat(coll, "murka", 2, [])
            assert app.delete_all(coll) == 1
            assert app.read_all(coll) == []
        finally:
            coll.drop()
    print("MongoDB: усі CRUD-операції — OK")

if __name__ == "__main__":
    try:
        verify_postgres()
        verify_mongo()
    except Exception as exc:
        print("Перевірка не пройшла:", type(exc).__name__, file=sys.stderr)
        sys.exit(1)
