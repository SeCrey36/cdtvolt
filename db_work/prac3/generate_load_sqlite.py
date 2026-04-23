"""генерирует нагрузку в sqlite до указанной цели.

использование: python3 generate_load_sqlite.py --target 500000
"""
import sqlite3
from pathlib import Path
import argparse
import random
import time

try:
    from faker import Faker
    _HAS_FAKER = True
except Exception:
    _HAS_FAKER = False

DB = Path(__file__).parent / 'database.sqlite3'


def generate(target=500000, batch_size=1000):
    if not DB.exists():
        raise SystemExit(f'бд не найдена в {DB}; сначала создайте схему')

    fake = Faker() if _HAS_FAKER else None
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute('SELECT COUNT(*) FROM enrollments')
    current = cur.fetchone()[0]
    print('текущих enrollments:', current)
    to_create = max(0, target - current)
    if to_create == 0:
        print('цель уже достигнута')
        conn.close()
        return

    cur.execute('SELECT id FROM users')
    user_ids = [r[0] for r in cur.fetchall()]
    cur.execute('SELECT id FROM timeslots')
    timeslot_ids = [r[0] for r in cur.fetchall()]
    if not timeslot_ids:
        raise SystemExit('таймслоты не найдены; создайте курсы/таймслоты сначала')

    inserted = 0
    start = time.perf_counter()
    while inserted < to_create:
        batch = []
        for _ in range(min(batch_size, to_create - inserted)):
            if user_ids and random.random() < 0.8:
                user = random.choice(user_ids)
            else:
                user = None
            name = fake.name() if fake else f'Guest {random.randint(1,10000000)}'
            phone = fake.phone_number() if fake else f'+100000{random.randint(1000,9999)}'
            email = fake.email() if fake else f'user{random.randint(1,10000000)}@example.com'
            created_at = fake.date_time_between(start_date='-3y', end_date='now').isoformat() if fake else time.strftime('%Y-%m-%dT%H:%M:%S')
            data_consent = 1
            batch.append((user, name, phone, email, '', '', created_at, 0, None, None, data_consent))

        cur.executemany('''INSERT INTO enrollments(user_id,student_name,student_phone,student_email,student_comment,feedback,created_at,is_approved,approved_by,approved_at,data_consent)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?)''', batch)
        conn.commit()

        cur.execute('SELECT last_insert_rowid()')
        last = cur.fetchone()[0]
        first = last - len(batch) + 1
        links = []
        tid_counts = {}
        for eid in range(first, last+1):
            tid = random.choice(timeslot_ids)
            links.append((eid, tid))
            tid_counts[tid] = tid_counts.get(tid, 0) + 1

        cur.executemany('INSERT INTO enrollment_timeslots(enrollment_id,timeslot_id) VALUES(?,?)', links)
        for tid, cnt in tid_counts.items():
            cur.execute('UPDATE timeslots SET booked_seats = booked_seats + ? WHERE id = ?', (cnt, tid))
        conn.commit()

        inserted += len(batch)
        if inserted % (10 * batch_size) == 0:
            elapsed = time.perf_counter() - start
            print(f'вставлено {inserted}/{to_create} (время {elapsed:.1f}s)')

    total_elapsed = time.perf_counter() - start
    print(f'вставлено {inserted} записей за {total_elapsed:.1f}s')
    conn.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--target', type=int, default=500000)
    p.add_argument('--batch', type=int, default=1000)
    args = p.parse_args()
    generate(target=args.target, batch_size=args.batch)
