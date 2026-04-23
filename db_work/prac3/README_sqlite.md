prac3 sqlite
=============

скрипты для работы с sqlite: создание схемы, заполнение, генерация нагрузки и тест производительности.

как запустить:

```bash
cd /Users/a123/work/cdtvolt
python3 db_work/prac3/create_schema_sqlite.py
python3 db_work/prac3/populate_sqlite.py --count 10000
python3 db_work/prac3/generate_load_sqlite.py --target 500000 --batch 2000
python3 db_work/prac3/test_query_perf_sqlite.py
```

результаты сохраняются в `db_work/prac3/perf_results_prac3.json`.
