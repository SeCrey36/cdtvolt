# Education Platform

Репозиторий проекта: https://github.com/SeCrey36/cdtvolt

## Что есть в проекте

- Django 5 + DRF + JWT
- API-документация Swagger
- Админка для работы с курсами, слотами и заявками
- Генерация договора из шаблона `contract.docx` (через `docxtpl`)

## Локальный запуск (основной, без Docker)

Рабочая директория проекта Django:

```bash
cd education_platform
```

Создайте и активируйте виртуальное окружение:

```bash
python3 -m venv ../.venv
source ../.venv/bin/activate
```

Установите зависимости:

```bash
pip install -r requirements.txt
```

Подготовьте `.env`:

```bash
cp .env.example .env
```

Примените миграции:

```bash
python manage.py migrate
```

Создайте администратора:

```bash
python manage.py createsuperuser
```

Запустите сервер:

```bash
python manage.py runserver
```

Откройте:

- Главная: `http://127.0.0.1:8000/`
- Админка: `http://127.0.0.1:8000/admin/`
- Swagger: `http://127.0.0.1:8000/swagger/`

## Запуск через Docker (опционально)

Подробные команды для Docker (логи, shell, backup SQLite, createsuperuser):

- `README_DOCKER.md`

Из корня репозитория:

```bash
docker compose up --build
```

После старта приложение доступно на `http://127.0.0.1:8000/`.

Остановить контейнеры:

```bash
docker compose down
```

## Договоры (`contract.docx`)

По умолчанию шаблон ищется в:

`education_platform/templates/contract.docx`

Либо можно задать путь через переменную окружения:

`CONTRACT_TEMPLATE_PATH=/absolute/path/to/contract.docx`

## JWT в Swagger

1. Получите токен через `POST /api/auth/login/`.
2. Нажмите `Authorize` в Swagger.
3. Введите: `Bearer <ваш_access_token>`.