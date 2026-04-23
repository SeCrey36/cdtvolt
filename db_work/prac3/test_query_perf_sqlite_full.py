"""полный тест производительности для sqlite: count(*) + explain, без лимита.

результаты в perf_results_prac3_full.json
"""
import sqlite3
from pathlib import Path
import time
import json

DB = Path(__file__).parent / 'database.sqlite3'
OUT = Path(__file__).parent / 'perf_results_prac3_full.json'

COUNT_QUERY = '''
SELECT COUNT(*)
FROM enrollments e
JOIN enrollment_timeslots et ON et.enrollment_id = e.id
JOIN timeslots t ON t.id = et.timeslot_id
JOIN courses c ON c.id = t.course_id
WHERE c.title LIKE 'Course %' AND e.data_consent=1
  AND date(e.created_at) >= date('2023-01-01')
  AND t.day_of_week IN (1,2,3);
'''

INDEX_STEPS = [
    ('baseline', []),
    ('index_courses_title', ["CREATE INDEX IF NOT EXISTS idx_courses_title ON courses(title);"]),
    ('add_where_indexes', [
        "CREATE INDEX IF NOT EXISTS idx_enrollments_created_at ON enrollments(created_at);",
        "CREATE INDEX IF NOT EXISTS idx_enrollments_data_consent ON enrollments(data_consent);",
        "CREATE INDEX IF NOT EXISTS idx_timeslots_day ON timeslots(day_of_week);",
    ]),
    ('composite_indexes', [
        "CREATE INDEX IF NOT EXISTS idx_enr_consent_created ON enrollments(data_consent, created_at);",
        "CREATE INDEX IF NOT EXISTS idx_timeslot_course_day ON timeslots(course_id, day_of_week);",
    ]),
    ('add_join_indexes', [
        "CREATE INDEX IF NOT EXISTS idx_timeslots_course ON timeslots(course_id);",
        "CREATE INDEX IF NOT EXISTS idx_et_timeslot ON enrollment_timeslots(timeslot_id);",
        "CREATE INDEX IF NOT EXISTS idx_et_enrollment ON enrollment_timeslots(enrollment_id);",
    ])
]


def explain_query_plan(conn, sql):
    cur = conn.execute('EXPLAIN QUERY PLAN ' + sql)
    rows = cur.fetchall()
    return [list(r) for r in rows]


def run_and_time(conn, sql):
    start = time.perf_counter()
    cur = conn.execute(sql)
    rows = cur.fetchall()
    elapsed = time.perf_counter() - start
    return elapsed, rows[0][0] if rows else 0


def apply_indexes(conn, stmts):
    cur = conn.cursor()
    for s in stmts:
        cur.execute(s)
    conn.commit()
    conn.execute('REINDEX')
    conn.commit()


def main():
    if not DB.exists():
        raise SystemExit('бд не найдена; сначала создайте и заполните её')

    results = []
    conn = sqlite3.connect(DB)

    for step_name, stmts in INDEX_STEPS:
        if stmts:
            apply_indexes(conn, stmts)
        plan = explain_query_plan(conn, COUNT_QUERY)
        elapsed, count = run_and_time(conn, COUNT_QUERY)
        results.append({
            'step': step_name,
            'num_indexes_applied': len(stmts),
            'plan': plan,
            'time_seconds': elapsed,
            'rows_count': count
        })
        print(f"шаг {step_name}: время={elapsed:.4f}s count={count}")

    conn.close()
    OUT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    print('записал результаты в', OUT)


if __name__ == '__main__':
    main()
