"""Print counts for core tables in db_work/database.sqlite3"""
import sqlite3
from pathlib import Path

DB = Path(__file__).parent / 'database.sqlite3'
TABLES = ['users','user_profiles','instructors','courses','course_instructors','timeslots','enrollments','enrollment_timeslots','news']


def main():
    if not DB.exists():
        print('Database not found at', DB)
        return
    conn = sqlite3.connect(DB)
    for t in TABLES:
        try:
            cur = conn.execute(f'SELECT COUNT(*) FROM {t}')
            cnt = cur.fetchone()[0]
        except Exception as e:
            cnt = f'error: {e}'
        print(f'{t}: {cnt}')
    conn.close()


if __name__ == '__main__':
    main()
