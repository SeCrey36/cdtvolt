"""создаёт sqlite базу и таблицы для prac3.

файл бд: db_work/prac3/database.sqlite3
"""
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent / 'database.sqlite3'


def create():
    if DB_PATH.exists():
        print(f"перезаписываю существующую бд: {DB_PATH}")
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('PRAGMA foreign_keys = ON;')

    # users
    cur.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT,
        is_active INTEGER DEFAULT 1
    );
    ''')

    # user_profiles
    cur.execute('''
    CREATE TABLE user_profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        phone TEXT,
        email_confirmed INTEGER DEFAULT 0,
        email_confirmation_token TEXT,
        email_confirmation_sent_at TEXT,
        created_at TEXT,
        updated_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')

    # instructors
    cur.execute('''
    CREATE TABLE instructors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        name TEXT,
        photo TEXT,
        bio TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')

    # courses
    cur.execute('''
    CREATE TABLE courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        image TEXT,
        price REAL DEFAULT 0.0,
        duration_minutes INTEGER DEFAULT 60,
        is_active INTEGER DEFAULT 1
    );
    ''')

    # course_instructors
    cur.execute('''
    CREATE TABLE course_instructors (
        course_id INTEGER,
        instructor_id INTEGER,
        PRIMARY KEY(course_id, instructor_id),
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
        FOREIGN KEY(instructor_id) REFERENCES instructors(id) ON DELETE CASCADE
    );
    ''')

    # timeslots
    cur.execute('''
    CREATE TABLE timeslots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_id INTEGER,
        day_of_week INTEGER,
        time_slot TEXT,
        max_seats INTEGER DEFAULT 10,
        booked_seats INTEGER DEFAULT 0,
        room TEXT,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
    );
    ''')

    cur.execute('CREATE UNIQUE INDEX IF NOT EXISTS ux_timeslot_course_day_time ON timeslots(course_id, day_of_week, time_slot);')

    # enrollments
    cur.execute('''
    CREATE TABLE enrollments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        student_name TEXT,
        student_phone TEXT,
        student_email TEXT,
        student_comment TEXT,
        feedback TEXT,
        created_at TEXT,
        is_approved INTEGER DEFAULT 0,
        approved_by INTEGER,
        approved_at TEXT,
        data_consent INTEGER DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL,
        FOREIGN KEY(approved_by) REFERENCES users(id) ON DELETE SET NULL
    );
    ''')

    # enrollment_timeslots
    cur.execute('''
    CREATE TABLE enrollment_timeslots (
        enrollment_id INTEGER,
        timeslot_id INTEGER,
        PRIMARY KEY(enrollment_id, timeslot_id),
        FOREIGN KEY(enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE,
        FOREIGN KEY(timeslot_id) REFERENCES timeslots(id) ON DELETE CASCADE
    );
    ''')

    # news
    cur.execute('''
    CREATE TABLE news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        title TEXT,
        description TEXT,
        created_at TEXT,
        is_active INTEGER DEFAULT 1
    );
    ''')

    conn.commit()
    conn.close()
    print(f'создана sqlite бд: {DB_PATH}')


if __name__ == '__main__':
    create()
