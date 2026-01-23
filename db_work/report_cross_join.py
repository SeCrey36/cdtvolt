""" Примеры:
  python report_cross_join.py --generate
  python report_cross_join.py --generate --execute --limit 5
"""
import sqlite3
from pathlib import Path
import argparse
import json

DB = Path(__file__).parent / 'database.sqlite3'


def list_tables(conn):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
    return [r[0] for r in cur.fetchall()]


def build_sql(tables):
    if len(tables) < 2:
        return None
    return 'SELECT * FROM ' + ' CROSS JOIN '.join(tables)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--generate', action='store_true')
    p.add_argument('--execute', action='store_true')
    p.add_argument('--limit', type=int, default=10)
    args = p.parse_args()

    if not DB.exists():
        print('Database not found. Run create_schema.py first.')
        return

    conn = sqlite3.connect(DB)
    tbls = list_tables(conn)
    print('Tables:', ', '.join(tbls) or '(none)')

    if not args.generate:
        print('Use --generate to see CROSS JOIN SQL')
        conn.close()
        return

    sql = build_sql(tbls)
    if not sql:
        print('Need at least two tables to build CROSS JOIN')
        conn.close()
        return

    sql_l = sql + f' LIMIT {args.limit}'
    print('\nCROSS JOIN SQL:')
    print(sql_l)

    if args.execute:
        print('\nExecuting...')
        cur = conn.execute(sql_l)
        cols = [d[0] for d in cur.description] if cur.description else []
        for row in cur.fetchall():
            # print each row as JSON on its own line
            obj = {cols[i]: row[i] for i in range(len(cols))} if cols else {'row': list(row)}
            print(json.dumps(obj, ensure_ascii=False))

    conn.close()


if __name__ == '__main__':
    main()
