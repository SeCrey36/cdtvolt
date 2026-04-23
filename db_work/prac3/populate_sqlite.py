"""заполняет sqlite бд тестовыми данными (users, courses, timeslots, enrollments).

использование: python3 populate_sqlite.py --count 10000
"""
import sqlite3
from pathlib import Path
from faker import Faker
import random
import argparse
from datetime import datetime

DB_PATH = Path(__file__).parent / 'database.sqlite3'


def populate(enrollment_count=10000):
    fake = Faker()
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # пользователи
    users = []
    for _ in range(500):
        username = fake.user_name()
        email = fake.email()
        users.append((username, email, 1))
    cur.executemany('INSERT INTO users(username,email,is_active) VALUES(?,?,?)', users)
    conn.commit()

    cur.execute('SELECT id FROM users')
    user_ids = [r[0] for r in cur.fetchall()]

    # профили
    profiles = []
    for uid in user_ids[:300]:
        profiles.append((uid, fake.phone_number(), 1, '', '', datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
    cur.executemany('''INSERT INTO user_profiles(user_id,phone,email_confirmed,email_confirmation_token,email_confirmation_sent_at,created_at,updated_at)
                       VALUES(?,?,?,?,?,?,?)''', profiles)
    conn.commit()

    # преподаватели
    instr = []
    instr_user_ids = user_ids[300:380]
    for uid in instr_user_ids:
        instr.append((uid, fake.name(), '', fake.text(max_nb_chars=200)))
    cur.executemany('INSERT INTO instructors(user_id,name,photo,bio) VALUES(?,?,?,?)', instr)
    conn.commit()

    cur.execute('SELECT id FROM instructors')
    instr_ids = [r[0] for r in cur.fetchall()]

    # курсы
    courses = []
    for i in range(200):
        courses.append((f"Course {i+1}", fake.text(max_nb_chars=200), '', round(random.uniform(0, 500), 2), random.choice([45,60,90]), 1))
    cur.executemany('INSERT INTO courses(title,description,image,price,duration_minutes,is_active) VALUES(?,?,?,?,?,?)', courses)
    conn.commit()

    cur.execute('SELECT id FROM courses')
    course_ids = [r[0] for r in cur.fetchall()]

    # привязки преподавателей к курсам
    ci = []
    for c in course_ids:
        iid = random.choice(instr_ids) if instr_ids else None
        if iid:
            ci.append((c, iid))
    cur.executemany('INSERT OR IGNORE INTO course_instructors(course_id,instructor_id) VALUES(?,?)', ci)
    conn.commit()

    # таймслоты
    timeslot_values = []
    time_choices = ['8-10','10-12','12-14','14-16','16-18','18-20','20-22']
    for c in course_ids:
        for day in range(5):
            ts = random.choice(time_choices)
            timeslot_values.append((c, day, ts, 10, 0, f'Room {random.randint(1,10)}', 1))
    cur.executemany('''INSERT INTO timeslots(course_id,day_of_week,time_slot,max_seats,booked_seats,room,is_active)
                       VALUES(?,?,?,?,?,?,?)''', timeslot_values)
    conn.commit()

    cur.execute('SELECT id FROM timeslots')
    timeslot_ids = [r[0] for r in cur.fetchall()]

    # новости
    news_items = []
    for i in range(20):
        news_items.append((fake.url(), fake.sentence(nb_words=6), fake.text(max_nb_chars=200), datetime.utcnow().isoformat(), 1))
    cur.executemany('INSERT INTO news(url,title,description,created_at,is_active) VALUES(?,?,?,?,?)', news_items)
    conn.commit()

    # создаём enrollments и связи
    print(f'создаю {enrollment_count} записей enrollments...')
    batch = []
    inserted = 0
    for i in range(enrollment_count):
        if random.random() < 0.8 and user_ids:
            user = random.choice(user_ids)
        else:
            user = None
        student_name = fake.name()
        student_phone = fake.phone_number()
        student_email = fake.email()
        created_at = datetime.utcnow().isoformat()
        is_approved = 0
        approved_by = None
        approved_at = None
        data_consent = 1
        batch.append((user, student_name, student_phone, student_email, '', '', created_at, is_approved, approved_by, approved_at, data_consent))

        if len(batch) >= 500:
            cur.executemany('''INSERT INTO enrollments(user_id,student_name,student_phone,student_email,student_comment,feedback,created_at,is_approved,approved_by,approved_at,data_consent)
                               VALUES(?,?,?,?,?,?,?,?,?,?,?)''', batch)
            conn.commit()
            cur.execute('SELECT last_insert_rowid()')
            last_id = cur.fetchone()[0]
            first_id = last_id - len(batch) + 1
            link_rows = []
            for eid in range(first_id, last_id + 1):
                tid = random.choice(timeslot_ids)
                link_rows.append((eid, tid))
                cur.execute('UPDATE timeslots SET booked_seats = booked_seats + 1 WHERE id = ?', (tid,))
            cur.executemany('INSERT INTO enrollment_timeslots(enrollment_id,timeslot_id) VALUES(?,?)', link_rows)
            conn.commit()
            inserted += len(batch)
            batch = []

    if batch:
        cur.executemany('''INSERT INTO enrollments(user_id,student_name,student_phone,student_email,student_comment,feedback,created_at,is_approved,approved_by,approved_at,data_consent)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?)''', batch)
        conn.commit()
        cur.execute('SELECT last_insert_rowid()')
        last_id = cur.fetchone()[0]
        first_id = last_id - len(batch) + 1
        link_rows = []
        for eid in range(first_id, last_id + 1):
            tid = random.choice(timeslot_ids)
            link_rows.append((eid, tid))
            cur.execute('UPDATE timeslots SET booked_seats = booked_seats + 1 WHERE id = ?', (tid,))
        cur.executemany('INSERT INTO enrollment_timeslots(enrollment_id,timeslot_id) VALUES(?,?)', link_rows)
        conn.commit()
        inserted += len(batch)

    print(f'вставлено enrollments: {inserted}')
    conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=10000)
    args = parser.parse_args()
    if not DB_PATH.exists():
        print('бд не найдена, запустите сначала create_schema_sqlite.py')
    else:
        populate(enrollment_count=args.count)
