## Education Platform – AI Coding Guide

- **Stack & Scope**: Django 5 project `education_platform` with single app `courses`. REST API (DRF + SimpleJWT + drf_yasg) and server-rendered pages share the same data models in `courses/models.py`.

- **Data Model**: `UserProfile` extends `auth.User` with phone + email confirmation token; `Instructor` links one-to-one to User; `Course` has many-to-many instructors; `TimeSlot` represents scheduled slots (day/time, capacity counters, unique per course/day/time); `Enrollment` ties a user + selected slots and mirrors student contact info; `News` stores external links.

- **Permissions & Auth**: DRF default permission is `IsAuthenticated` globally (`settings.py`). Public endpoints set `AllowAny` explicitly (courses list/detail, slots, auth/register/login/confirm/resend). JWT auth via SimpleJWT; access lifetime is 1 day and refresh 7 days (see `SIMPLE_JWT`). Email confirmation is required before creating enrollments.

- **API Surface** (`courses/urls_api.py`): auth (`/api/auth/register|login|refresh|logout|confirm-email[/<token>]`), profile (`/api/profile`, change password, enrollments), enrollments create (`/api/enrollments/create/`), courses catalog and slots (`/api/courses/`, `/api/courses/<id>/`, `/slots`, `/available-slots`). Swagger UI at `/swagger/`, Redoc at `/redoc/` (uses `courses/swagger_config.py`).

- **Serializers/Flows** (`courses/serializers.py`): registration creates `UserProfile`, generates + emails confirmation token (Gmail SMTP settings in `settings.py`). `CreateEnrollmentSerializer` validates email confirmed, slot availability, and that all slots belong to one course; auto-fills student data from user and increments `booked_seats` after assigning slots. Keep `booked_seats` in sync when altering enrollment creation logic.

- **Views (HTML)** (`courses/views.py`): `CourseDetailView` builds `schedule_data` matrix (days x time slots) for templates; basic pages `index/login/register/profile/news/api_test` render static templates in `courses/templates/courses/`. Public course detail URL `course/<pk>/` reuses the CBV.

- **Admin Customizations** (`courses/admin.py`): course admin auto-creates default time slots (Mon–Fri 10-12) on first save when flag enabled. TimeSlot inline enforces unique day/time per course. Enrollment admin adjusts `booked_seats` deltas when slot assignments change and stamps approver/timestamp when `is_approved` toggles. Avoid manual writes to `booked_seats`; use provided save hooks.

- **Settings & Environment** (`education_platform/settings.py`): DEBUG True, SQLite default. SECRET_KEY and `EMAIL_HOST_PASSWORD` are blank—set via env for real use. Static files served from `/static/` with project-level `static/`; media under `/media/`. Global templates directory `templates/` plus app templates via `APP_DIRS`.

- **Developer Commands** (run from `education_platform/`):
  - `python manage.py migrate` to init DB (SQLite by default).
  - `python manage.py createsuperuser` to access admin.
  - `python manage.py runserver` for local dev; Swagger at `/swagger/`.
  - `python manage.py test courses` (tests placeholder).

- **Conventions & Patterns**: API views mostly DRF generics; public endpoints set `permission_classes = (AllowAny,)` inline. Time slot availability uses `booked_seats < max_seats`; helper properties `free_seats`/`has_free_seats` in `TimeSlot`. Course instructor names via `Course.get_instructors_names()` reused in admin lists.

- **Email Confirmation UX**: GET `/api/auth/confirm-email/<token>/` marks confirmed; resend via `/api/auth/resend-confirmation/` regenerates token and logs email content to console if SMTP fails. Keep tokens on `UserProfile` (`generate_confirmation_token`, `confirm_email`).

- **Front-end Assets**: Project-level `templates/` and `static/` exist; app-specific assets under `courses/templates/courses/` and `courses/static/courses/` (CSS/JS). Base admin CSS override in `static/admin/css/custom.css`.

- **Gotchas**: Swagger description mentions 15-minute tokens but actual lifetimes are 1 day/7 days; align docs if you change settings. Enrollment save hooks and serializer both manage slot counters—if you change creation flow, ensure counters remain consistent. Default DRF permission blocks new endpoints unless `AllowAny` set explicitly.