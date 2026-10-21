-- Приклади для user_id=1 та task_id=1 (після першого seed).
-- Змінні запити виконуються всередині транзакції та відкочуються наприкінці.
-- Щоб зберегти зміни, свідомо замініть останній ROLLBACK на COMMIT.
BEGIN;

-- 1. Всі завдання конкретного користувача.
SELECT * FROM tasks WHERE user_id = 1 ORDER BY id;

-- 2. Завдання зі статусом new: підзапит.
SELECT * FROM tasks WHERE status_id = (SELECT id FROM status WHERE name = 'new') ORDER BY id;

-- 3. Оновлення статусу конкретного завдання.
UPDATE tasks SET status_id = (SELECT id FROM status WHERE name = 'in progress')
WHERE id = 1 RETURNING *;

-- 4. Користувачі без завдань: NOT IN + підзапит.
SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM tasks) ORDER BY id;

-- 5. Нове завдання конкретному користувачу.
INSERT INTO tasks(title,description,status_id,user_id)
VALUES ('Learn SQL', 'Practice joins and subqueries',
        (SELECT id FROM status WHERE name = 'new'), 1) RETURNING *;

-- 6. Усі незавершені завдання.
SELECT t.* FROM tasks t JOIN status s ON s.id = t.status_id
WHERE s.name <> 'completed' ORDER BY t.id;

-- 7. Видалення конкретного завдання.
DELETE FROM tasks WHERE id = 1 RETURNING *;

-- 8. Пошук користувачів за електронною поштою (LIKE).
SELECT * FROM users WHERE email LIKE '%@example.com' ORDER BY id;

-- 9. Оновлення імені користувача.
UPDATE users SET fullname = 'Updated User' WHERE id = 1 RETURNING *;

-- 10. Кількість завдань для кожного статусу, включно з нульовою.
SELECT s.name, COUNT(t.id) AS task_count
FROM status s LEFT JOIN tasks t ON t.status_id = s.id
GROUP BY s.id, s.name ORDER BY s.id;

-- 11. Завдання користувачів з доменом example.com.
SELECT t.*, u.email FROM tasks t JOIN users u ON u.id = t.user_id
WHERE u.email LIKE '%@example.com' ORDER BY t.id;

-- 12. Відсутній опис: NULL, порожній рядок або пробіли.
SELECT * FROM tasks WHERE description IS NULL OR BTRIM(description) = '' ORDER BY id;

-- 13. Користувачі і завдання in progress (INNER JOIN).
SELECT u.id AS user_id, u.fullname, t.id AS task_id, t.title, s.name AS status
FROM users u INNER JOIN tasks t ON t.user_id = u.id
INNER JOIN status s ON s.id = t.status_id
WHERE s.name = 'in progress' ORDER BY u.id, t.id;

-- 14. Користувачі та кількість завдань, включно з користувачами без завдань.
SELECT u.id, u.fullname, COUNT(t.id) AS task_count
FROM users u LEFT JOIN tasks t ON t.user_id = u.id
GROUP BY u.id, u.fullname ORDER BY u.id;

ROLLBACK;
