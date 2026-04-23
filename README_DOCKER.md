# Docker Guide (Education Platform)

про запуск и обслуживание проекта через Docker

## 1. Быстрый старт

Из корня репозитория:

```bash
docker compose up --build
```

Приложение будет доступно по адресу:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/admin/`
- `http://127.0.0.1:8000/swagger/`

Остановить:

```bash
docker compose down
```

## 2. Полезные команды

Выполнить миграции:

```bash
docker compose exec web python manage.py migrate
```

Создать суперпользователя:

```bash
docker compose exec web python manage.py createsuperuser
```

Открыть Django shell:

```bash
docker compose exec web python manage.py shell
```

Запустить проверку проекта:

```bash
docker compose exec web python manage.py check
```

Собрать статику:

```bash
docker compose exec web python manage.py collectstatic --noinput
```

## 3. Логи и отладка

Логи всех сервисов:

```bash
docker compose logs -f
```

Логи только Django-сервиса:

```bash
docker compose logs -f web
```

Зайти в shell контейнера:

```bash
docker compose exec web sh
```

Проверить установленные пакеты внутри контейнера:

```bash
docker compose exec web pip list
```

## 4. Работа с базой SQLite

В проекте используется файл `education_platform/db.sqlite3`.

Создать резервную копию на хосте:

```bash
cp education_platform/db.sqlite3 education_platform/db.sqlite3.bak
```

Восстановить из бэкапа:

```bash
cp education_platform/db.sqlite3.bak education_platform/db.sqlite3
```

## 5. Шаблон договора `contract.docx`

По умолчанию генератор ищет шаблон по пути:

- `/app/templates/contract.docx` (на хосте это `education_platform/templates/contract.docx`)

Можно переопределить через переменную:

- `CONTRACT_TEMPLATE_PATH`

В Docker Compose она задаётся в `docker-compose.yml`.
