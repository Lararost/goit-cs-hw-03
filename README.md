# goit-cs-hw-03

Домашня робота «Вступ до вивчення систем управління базами даних».
Python 3.11+, PostgreSQL 15, PyMongo, Faker.

## Структура

```text
task_01/create_tables.py  — створення трьох таблиць
task_01/seed.py           — генерація даних Faker
task_01/queries.sql       — усі 14 запитів у порядку умови
task_02/main.py           — інтерактивний CRUD котів MongoDB
verify.py                — перевірка реальних баз після запуску
```

## Запуск через Docker (рекомендовано)

Відкрити Terminal у папці `goit-cs-hw-03`. Docker Desktop має працювати.
Python на Mac встановлювати не потрібно: скрипти виконуються у контейнері.
Бази використовують окремі порти і не конфліктують із попереднім ДЗ.

```bash
docker compose up -d --wait postgres mongo
docker compose build python
docker compose run --rm python python task_01/create_tables.py
docker compose run --rm python python task_01/seed.py
```

Виконати всі 14 SQL-запитів і зберегти реальний вивід:

```bash
docker compose exec -T postgres psql -U postgres -d task_manager -v ON_ERROR_STOP=1 -a < task_01/queries.sql > sql_results.txt
```

У файлі є BEGIN/ROLLBACK: INSERT, UPDATE і DELETE реально виконуються,
але зміни даних відкочуються наприкінці. Для збереження змін можна
замінити останній ROLLBACK на COMMIT. SERIAL-послідовність може зростати
навіть після ROLLBACK. Приклади використовують id=1 із першого seed.
Для інших даних замініть ідентифікатори на наявні.

Перевірка схеми, каскадного видалення, SQL та CRUD на реальних базах:

```bash
docker compose run --rm python python verify.py
```

Інтерактивний застосунок MongoDB:

```bash
docker compose run --rm python python task_02/main.py
```

Для створення документа обрати пункт 3 і ввести:

```text
Ім'я: barsik
Вік: 3
Характеристики через кому: ходить в капці, дає себе гладити, рудий
```

MongoDB автоматично створить базу `hw03` і колекцію `cats` після запису.
Пункт 1 показує всіх котів, 2 шукає за ім'ям, 4 змінює вік,
5 додає характеристику без дублювання, 6 видаляє кота,
7 видаляє всі документи після введення DELETE. Пункт 0 — вихід.
Імена нормалізуються до нижнього регістру; унікальний індекс не дозволяє
створити двох котів з однаковим ім'ям. Невід'ємний цілий вік перевіряється.
Помилки введення, дублікати, помилки сервера та відсутність запису оброблені.

На твоєму Mac команда `docker` може бути недоступна у PATH.
Перед командами вище виконай у поточному вікні Terminal:

```bash
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

## PostgreSQL

users: SERIAL PK, fullname VARCHAR(100), email VARCHAR(100) UNIQUE.
status: SERIAL PK, name VARCHAR(50) UNIQUE.
tasks: SERIAL PK, title VARCHAR(100), description TEXT, зовнішні ключі
status_id та user_id. Видалення користувача каскадно видаляє його tasks.
Seed додає 20 користувачів і 60 завдань; три користувачі гарантовано
не мають завдань, є всі статуси, адреси example.com і порожні описи.
Повторний seed додає дані, а не очищає їх. Статуси не дублюються.
Параметри у Python передаються через placeholders, не через SQL-конкатенацію.

## Локальний Python / MongoDB Atlas (альтернатива)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Для баз із Docker та Python на комп'ютері адреси за замовчуванням:
PostgreSQL `localhost:5433/task_manager`, MongoDB `localhost:27018`.

```bash
python task_01/create_tables.py
python task_01/seed.py
python task_02/main.py
```

Можна задати `DATABASE_URL`, `MONGODB_URI`, `MONGODB_DB` через змінні
середовища. Для Atlas задати MONGODB_URI з Atlas, користувача БД і
дозволену IP-адресу в Network Access. Не додавати справжні паролі до GitHub.
При запуску Python у Docker Compose використовуються адреси сервісів
`postgres:5432` і `mongo:27017`, які Compose задає автоматично.

## Зупинка та діагностика

```bash
docker compose ps
docker compose logs --tail=80 postgres mongo
docker compose down
```

`down` зберігає дані в volumes. Навчальні паролі у Compose призначені
лише для локального середовища; порти прив'язані до 127.0.0.1.
При конфлікті порту змінити ліву частину mapping у Compose.

## Межі перевірки комплекту

Під час підготовки перевірено Python-синтаксис, PostgreSQL-синтаксис
DDL і всіх 14 запитів, структуру Compose та CRUD на mongomock.
Mongomock — емулятор, не реальний сервер MongoDB. Запуск Docker та
інтеграційний verify.py потрібно виконати на комп'ютері з Docker перед здачею.
Файл sql_results.txt створюється лише реальним запуском команди вище.

## Здача

Завантажити вміст цієї папки в публічний репозиторій goit-cs-hw-03.
Прикріпити ZIP з назвою ДЗ3_ПІБ та посилання на репозиторій у LMS.
У коментарі обрати підхід: прийняти першу прохідну оцінку або доопрацьовувати
роботу для вищого бала за фідбеком ментора. Це особистий вибір автора.
