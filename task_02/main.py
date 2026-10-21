"""Консольний CRUD котів у MongoDB; підтримує локальний MongoDB та Atlas."""
import os
import sys
from bson.json_util import dumps
from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError, DuplicateKeyError

def valid_name(name):
    """Нормалізувати ім'я: пробіли по краях і регістр не розрізняються."""
    value = name.strip().lower()
    if not value:
        raise ValueError("Ім'я не може бути порожнім.")
    return value

def valid_age(age):
    """Вік має бути цілим невід'ємним числом."""
    value = str(age).strip()
    if not value.isdecimal():
        raise ValueError("Вік має бути цілим невід'ємним числом.")
    return int(value)

def create_cat(collection, name, age, features):
    """Створити кота; MongoDB автоматично додає ObjectId у _id."""
    if not isinstance(features, list) or any(not isinstance(f, str) or not f.strip() for f in features):
        raise ValueError("Характеристики мають бути списком непорожніх рядків.")
    return collection.insert_one({"name": valid_name(name), "age": valid_age(age),
                                  "features": list(dict.fromkeys(f.strip() for f in features))}).inserted_id

def read_all(collection):
    """Повернути всіх котів, відсортованих за ім'ям."""
    return list(collection.find().sort("name", ASCENDING))

def read_by_name(collection, name):
    """Знайти одного кота за ім'ям або повернути None."""
    return collection.find_one({"name": valid_name(name)})

def update_age(collection, name, age):
    """Оновити вік; matched_count показує, чи знайдено кота."""
    return collection.update_one({"name": valid_name(name)}, {"$set": {"age": valid_age(age)}})

def add_feature(collection, name, feature):
    """Додати характеристику без дублювання через $addToSet."""
    feature = feature.strip()
    if not feature:
        raise ValueError("Характеристика не може бути порожньою.")
    return collection.update_one({"name": valid_name(name)}, {"$addToSet": {"features": feature}})

def delete_by_name(collection, name):
    """Видалити кота за ім'ям."""
    return collection.delete_one({"name": valid_name(name)}).deleted_count

def delete_all(collection):
    """Видалити документи лише з поточної колекції котів."""
    return collection.delete_many({}).deleted_count

def print_documents(documents):
    """Вивести BSON/ObjectId у читабельному JSON."""
    if documents is None or documents == []:
        print("Записів не знайдено.")
    else:
        print(dumps(documents, ensure_ascii=False, indent=2))

def menu(collection):
    """Інтерактивне введення імені, віку та характеристик користувачем."""
    while True:
        print("\n1 — усі коти; 2 — пошук; 3 — додати кота; 4 — змінити вік;"
              "\n5 — додати характеристику; 6 — видалити кота; 7 — видалити всіх; 0 — вихід")
        choice = input("Ваш вибір: ").strip()
        try:
            if choice == "0":
                return
            if choice == "1":
                print_documents(read_all(collection))
            elif choice == "2":
                print_documents(read_by_name(collection, input("Ім'я: ")))
            elif choice == "3":
                name = input("Ім'я: ")
                age = input("Вік: ")
                features = [s.strip() for s in input("Характеристики через кому: ").split(",") if s.strip()]
                print("Створено:", create_cat(collection, name, age, features))
            elif choice in ("4", "5"):
                name = input("Ім'я: ")
                result = (update_age(collection, name, input("Новий вік: ")) if choice == "4"
                          else add_feature(collection, name, input("Нова характеристика: ")))
                print("Кота не знайдено." if result.matched_count == 0 else
                      ("Оновлено." if result.modified_count else "Значення вже збережено."))
            elif choice == "6":
                print("Видалено записів:", delete_by_name(collection, input("Ім'я: ")))
            elif choice == "7":
                if input("Для видалення ВСІХ котів введіть DELETE: ").strip() == "DELETE":
                    print("Видалено записів:", delete_all(collection))
                else:
                    print("Скасовано.")
            else:
                print("Оберіть пункт від 0 до 7.")
        except DuplicateKeyError:
            print("Кіт із таким ім'ям уже існує.")
        except ValueError as exc:
            print("Помилка введення:", exc)
        except PyMongoError:
            print("Операція MongoDB не вдалася. Перевірте з'єднання та права доступу.")

def main():
    """Перевірити сервер, створити індекс і відкрити меню."""
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27018/")
    try:
        with MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000,
                         socketTimeoutMS=10000) as client:
            client.admin.command("ping")
            collection = client[os.getenv("MONGODB_DB", "hw03")]["cats"]
            collection.create_index("name", unique=True)
            menu(collection)
    except PyMongoError:
        print("Не вдалося підключитися або підготувати MongoDB. Перевірте MONGODB_URI, сервер та унікальність імен.", file=sys.stderr)
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nРоботу завершено.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
