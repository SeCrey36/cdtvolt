"""python db_work/run_queries.py
Outputs saved to `db_work/out/query_N.json` (and .csv if requested).
"""
import sqlite3
from pathlib import Path
import json
import csv

ROOT = Path(__file__).parent
DB = ROOT / 'database.sqlite3'
SQL = ROOT / 'queries_prac2.sql'
OUT = ROOT / 'out'
OUT.mkdir(exist_ok=True)


def split_statements(sql_text):
    return [s.strip() for s in sql_text.split(';') if s.strip()]


def norm(val):
    if val is None:
        return None
    if isinstance(val, (bytes, bytearray)):
        try:
            return val.decode('utf-8')
        except Exception:
            return str(val)
    return val


def run():
    if not DB.exists():
        print('Database not found at', DB)
        return
    if not SQL.exists():
        print('SQL file not found at', SQL)
        return

    sql_text = SQL.read_text(encoding='utf-8')
    stmts = split_statements(sql_text)
    conn = sqlite3.connect(DB)
    for i, s in enumerate(stmts, 1):
        try:
            cur = conn.execute(s)
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchall()
            records = [ {cols[j]: norm(rows[r][j]) for j in range(len(cols))} for r in range(len(rows)) ] if cols else [ {'row': list(r)} for r in rows ]

            json_path = OUT / f'query_{i}.json'
            json_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')

        
            if cols:
                csv_path = OUT / f'query_{i}.csv'
                with csv_path.open('w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(cols)
                    for r in rows:
                        writer.writerow([norm(x) for x in r])

            print(f'Query {i}: {len(records)} row(s) -> {json_path}')
        except Exception as e:
            print(f'Query {i} error:', e)
    conn.close()


if __name__ == '__main__':
    run()
