# db_work — локальная копия БД + скрипты для работы

Расположение: `db_work/` в корне репозитория.

 Скрипты:

 - `create_schema.py` — создаёт `db_work/database.sqlite3` в папке `db_work`.
 - `populate.py` — заполняет `db_work/database.sqlite3` тестовыми данными (использует `Faker`).
 - `report_cross_join.py` — ранний инструмент для быстрых CROSS JOIN проверок.
 - `requirements.txt` — зависимости (Faker, tabulate, PyYAML — опционально).
 - `README.md` — (этот файл).

 Новые скрипты для практической работы (используют `db_work/database.sqlite3`):

 - `queries_prac2.sql` — примеры JOIN-запросов (INNER, LEFT, CROSS, агрегации, типовой запрос приложения).
 - `run_queries.py` — выполняет `queries_prac2.sql` и сохраняет результаты в `db_work/out/` (`.json` и `.csv`).
 - `check_counts.py` — печатает `COUNT(*)` для ключевых таблиц.

 Примеры команд (из корня репозитория):

 ```bash
 # создать/пересоздать БД
 python db_work/create_schema.py

 # установить зависимости
 python -m pip install -r db_work/requirements.txt

 # наполнить тестовыми данными (примерное число записей, может занять время)
 python db_work/populate.py --count 10000

 # проверить количество строк в таблицах
 python db_work/check_counts.py

 # выполнить примеры JOIN и сохранить результаты в db_work/out/
 python db_work/run_queries.py

 # Посмотреть файлы вывода
 ls -la db_work/out
 ```

 Что заскринить:
 - `python db_work/check_counts.py` — вывод счётчиков (покажет, что данных достаточно).
 - Содержимое `db_work/out/query_*.json` для нескольких примеров JOIN (пример вывода `run_queries.py`).
 - Пример выполнения типового запроса (один из `queries_prac2.sql`) и его результат.

Установка зависимостей (в виртуальном окружении):

```bash
python -m pip install -r db_work/requirements.txt
```

Примеры использования:

```bash
# Создать схему
python db_work/create_schema.py

# Наполнить данными (по умолчанию 10000 enrollments)
python db_work/populate.py --count 10000

# Сгенерировать CROSS JOIN SQL (не выполнять)
python db_work/report_cross_join.py --generate

# Сгенерировать и выполнить с лимитом 5 строк
python db_work/report_cross_join.py --generate --execute --limit 5
```

Внимание:
- Выполнение `CROSS JOIN` по многим таблицам может привести к очень большому результату. Используйте `--limit`.
